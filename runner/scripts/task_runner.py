"""Task runner."""

import csv
import datetime
import hashlib
import logging
import os
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path
from typing import IO, List, Optional

import requests
from flask import current_app as app
from jinja2 import Environment, PackageLoader, select_autoescape
from pathvalidate import sanitize_filename

from runner import db, redis_client
from runner.model import Task, TaskFile, TaskLog
from runner.scripts.em_cmd import Cmd
from runner.scripts.em_code import SourceCode
from runner.scripts.em_date import DateParsing
from runner.scripts.em_file import File, file_size
from runner.scripts.em_ftp import Ftp
from runner.scripts.em_messages import RunnerException, RunnerLog
from runner.scripts.em_params import ParamLoader
from runner.scripts.em_postgres import Postgres
from runner.scripts.em_python import PyProcesser
from runner.scripts.em_sftp import Sftp
from runner.scripts.em_smb import Smb
from runner.scripts.em_smtp import Smtp
from runner.scripts.em_sqlserver import SqlServer
from runner.scripts.em_ssh import Ssh
from runner.scripts.em_system import system_monitor
from runner.web.filters import datetime_format

sys.path.append(str(Path(__file__).parents[2]) + "/scripts")
from crypto import em_decrypt

env = Environment(
    loader=PackageLoader("runner", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


env.filters["datetime_format"] = datetime_format


# set the limit for a csv cell value to something massive.
# this is needed when users are building xml in a sql query
# and have one very large column.

MAX_INT = sys.maxsize

while True:
    # decrease the MAX_INT value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(MAX_INT)
        break
    except OverflowError:
        MAX_INT = int(MAX_INT / 10)


class Runner:
    """Group of functions used to run a task."""

    # pylint: disable=too-few-public-methods

    def __init__(self, task_id: int) -> None:
        """Set up class parameters.

        On sequence jobs, only the first enabled job in the
        sequence should be in the scheduler.
        """
        # Create id for the run instance and assign to tasks being run.
        my_hash = hashlib.sha256()
        my_hash.update(str(time.time() * 1000).encode("utf-8"))

        self.run_id = my_hash.hexdigest()[:10]

        task = Task.query.filter_by(id=task_id).first()

        self.source_files: List[IO[str]]
        self.output_files: List[str] = []

        print("starting task " + str(task.id))  # noqa: T001
        logging.info(
            "Runner: Starting task: %s, with run: %s",
            str(task.id),
            str(my_hash.hexdigest()[:10]),
        )

        # set status to running
        task.status_id = 1
        task.last_run_job_id = self.run_id
        task.last_run = datetime.datetime.now()
        db.session.commit()

        RunnerLog(task, self.run_id, 8, "Starting task!")

        self.task = task

        # If monitor fails then cancel task.
        try:
            system_monitor()

        except ValueError as message:
            RunnerException(self.task, self.run_id, 18, message)

        # create temp folder for output
        self.temp_path = Path(
            Path(__file__).parent.parent
            / "temp"
            / sanitize_filename(self.task.project.name)
            / sanitize_filename(self.task.name)
            / self.run_id
        )
        self.temp_path.mkdir(parents=True, exist_ok=True)

        RunnerLog(task, self.run_id, 8, "Loading parameters...")

        self.param_loader = ParamLoader(self.task, self.run_id)

        # load file/ run query/ etc to get some sort of data or process something.
        self.query_output_size: Optional[int] = None
        self.source_loader = SourceCode(self.task, self.run_id, self.param_loader)
        self.source_files = []
        self.__get_source()

        # any data post-processing
        if self.task.processing_type_id is not None:
            self.__process()

        # store output
        self.__store_files()

        # send confirmation/error emails
        self.__send_email()

        # any cleanup process. remove file from local storage
        self.__clean_up()

        RunnerLog(self.task, self.run_id, 8, "Completed task!")

        # remove any retry tracking
        redis_client.delete(f"runner_{task_id}_attempt")
        task.status_id = 4
        task.est_duration = (datetime.datetime.now() - task.last_run).total_seconds()

        # if this is a sequence job, trigger the next job.
        if task.project.sequence_tasks == 1:
            task_id_list = [
                x.id
                for x in Task.query.filter_by(enabled=1)
                .filter_by(project_id=task.project_id)
                .order_by(Task.order.asc(), Task.name.asc())  # type: ignore[union-attr]
                .all()
            ]
            # potentially the task was disabled while running
            # and removed from list. when that happens we should
            # quit.
            if task.id in task_id_list:
                next_task_id = task_id_list[
                    task_id_list.index(task.id) + 1 : task_id_list.index(task.id) + 2
                ]
                if next_task_id:

                    # trigger next task
                    RunnerLog(
                        self.task,
                        self.run_id,
                        8,
                        f"Triggering run of next sequence job: {next_task_id}.",
                    )

                    next_task = Task.query.filter_by(id=next_task_id[0]).first()

                    RunnerLog(
                        next_task,
                        None,
                        8,
                        f"Run triggered by previous sequence job: {task.id}.",
                    )

                    requests.get(app.config["RUNNER_HOST"] + "/" + str(next_task_id[0]))

                else:
                    RunnerLog(self.task, self.run_id, 8, "Sequence completed!")

        task.last_run_job_id = None
        task.last_run = datetime.datetime.now()
        db.session.commit()

    # pylint: disable=R1710
    def __get_source(self) -> None:

        if self.task.source_type_id == 1:  # sql

            external_db = self.task.source_database_conn
            try:
                RunnerLog(self.task, self.run_id, 8, "Loading query...")
                query = self.__get_query()
            except BaseException as e:
                raise RunnerException(
                    self.task, self.run_id, 8, f"Failed to load query.\n{e}"
                )

            RunnerLog(
                self.task, self.run_id, 8, "Starting query run, waiting for results..."
            )

            if external_db.database_type.id == 1:  # postgres
                try:
                    self.query_output_size, self.source_files = Postgres(
                        task=self.task,
                        run_id=self.run_id,
                        connection=em_decrypt(
                            external_db.connection_string, app.config["PASS_KEY"]
                        ),
                        directory=self.temp_path,
                    ).run(query)

                except ValueError as message:
                    raise RunnerException(self.task, self.run_id, 21, message)

                except BaseException as message:
                    raise RunnerException(
                        self.task, self.run_id, 21, f"Failed to run query.\n{message}"
                    )

            elif external_db.database_type.id == 2:  # mssql
                try:
                    self.query_output_size, self.source_files = SqlServer(
                        task=self.task,
                        run_id=self.run_id,
                        connection=em_decrypt(
                            external_db.connection_string, app.config["PASS_KEY"]
                        ),
                        directory=self.temp_path,
                    ).run(query)

                except ValueError as message:
                    raise RunnerException(self.task, self.run_id, 20, message)

                except BaseException as message:
                    raise RunnerException(
                        self.task, self.run_id, 20, f"Failed to run query.\n{message}"
                    )

            RunnerLog(
                self.task,
                self.run_id,
                8,
                f"Query completed.\nData file {self.source_files[0].name} created. Data size: {file_size(str(Path(self.source_files[0].name).stat().st_size))}.",
            )

        elif self.task.source_type_id == 2:  # smb file
            file_name = self.param_loader.insert_file_params(self.task.source_smb_file)
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            self.source_files = Smb(
                task=self.task,
                run_id=self.run_id,
                connection=self.task.source_smb_conn,
                directory=self.temp_path,
            ).read(file_name=file_name)

        elif self.task.source_type_id == 3:  # sftp file
            RunnerLog(self.task, self.run_id, 9, "Loading data from server...")
            file_name = self.param_loader.insert_file_params(self.task.source_sftp_file)
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            self.source_files = Sftp(
                task=self.task,
                run_id=self.run_id,
                connection=self.task.source_sftp_conn,
                directory=self.temp_path,
            ).read(file_name=file_name)

        elif self.task.source_type_id == 4:  # ftp file
            RunnerLog(self.task, self.run_id, 13, "Loading data from server...")
            file_name = self.param_loader.insert_file_params(self.task.source_ftp_file)
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            self.source_files = Ftp(
                task=self.task,
                run_id=self.run_id,
                connection=self.task.source_ftp_conn,
                directory=self.temp_path,
            ).read(file_name=file_name)

        elif self.task.source_type_id == 6:  # ssh command
            query = self.__get_query()

            Ssh(
                task=self.task,
                run_id=self.run_id,
                connection=self.task.source_ssh_conn,
                command=query,
            ).run()

    def __get_query(self) -> str:

        if self.task.source_query_type_id == 3:  # url
            query = self.source_loader.web_url(self.task.source_url)

        elif self.task.source_query_type_id == 1:  # gitlab url
            query = self.source_loader.gitlab(self.task.source_git)

        elif self.task.source_query_type_id == 4:  # code
            query = self.source_loader.source()

        elif self.task.source_query_type_id == 2:  # smb
            file_name = self.param_loader.insert_file_params(
                self.task.source_query_file
            )
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()
            query = self.source_loader.source(
                Path(
                    Smb(
                        task=self.task,
                        run_id=self.run_id,
                        directory=self.temp_path,
                        connection=self.task.query_source,
                    )
                    .read(file_name)[0]
                    .name
                ).read_text("utf8")
            )

        return query

    def __process(self) -> None:

        RunnerLog(self.task, self.run_id, 8, "Starting processing script...")
        # get processing script

        # 1 = smb
        # 2 = sftp
        # 3 = ftp
        # 4 = git url
        # 5 = other url
        # 6 = source code

        processing_script_name = self.temp_path / (self.run_id + ".py")

        my_file = ""
        if (
            self.task.processing_type_id == 1
            and self.task.processing_smb_id is not None
        ):
            file_name = self.param_loader.insert_file_params(self.task.source_smb_file)
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            my_file = Path(
                Smb(
                    task=self.task,
                    run_id=self.run_id,
                    directory=self.temp_path,
                    connection=self.task.processing_smb_conn,
                )
                .read(file_name)[0]
                .name
            ).read_text("utf8")

        elif (
            self.task.processing_type_id == 2
            and self.task.processing_sftp_id is not None
        ):
            file_name = self.param_loader.insert_file_params(
                self.task.processing_sftp_file
            )
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            my_file = Path(
                Sftp(
                    task=self.task,
                    run_id=self.run_id,
                    connection=self.task.processing_sftp_conn,
                    directory=self.temp_path,
                )
                .read(file_name=file_name)[0]
                .name
            ).read_text("utf8")

        elif (
            self.task.processing_type_id == 3
            and self.task.processing_ftp_id is not None
        ):
            file_name = self.param_loader.insert_file_params(
                self.task.processing_ftp_file
            )
            file_name = DateParsing(
                task=self.task,
                run_id=self.run_id,
                date_string=file_name,
            ).string_to_date()

            my_file = Path(
                Ftp(
                    task=self.task,
                    run_id=self.run_id,
                    connection=self.task.source_ftp_conn,
                    directory=self.temp_path,
                )
                .read(file_name=file_name)[0]
                .name
            ).read_text("utf8")

        elif self.task.processing_type_id == 4 and self.task.processing_git is not None:

            # if a dir is specified then download all files
            if (
                self.task.processing_command is not None
                and self.task.processing_command != ""
            ):
                try:
                    url = (
                        re.sub(
                            r"(https?://)(.+?)",
                            r"\1<username>:<password>@\2",
                            self.task.processing_git,
                            flags=re.IGNORECASE,
                        )
                        .replace(
                            "<username>", urllib.parse.quote(app.config["GIT_USERNAME"])
                        )
                        .replace(
                            "<password>", urllib.parse.quote(app.config["GIT_PASSWORD"])
                        )
                    )

                    cmd = (
                        "$(which git) clone -q --depth 1 "
                        + '--recurse-submodules --shallow-submodules %s "%s"'
                        % (url, str(self.temp_path))
                    )

                    Cmd(
                        self.task,
                        self.run_id,
                        cmd,
                        "Repo cloned.",
                        "Failed to clone repo: %s" % (self.task.processing_git,),
                    ).shell()

                # pylint: disable=broad-except
                except BaseException:
                    raise RunnerException(
                        self.task, self.run_id, 8, "Processor failed to clone repo."
                    )

            # otherwise get py file
            else:
                my_file = self.source_loader.gitlab(self.task.processing_git)

        elif self.task.processing_type_id == 5 and self.task.processing_url is not None:
            if self.task.processing_command is not None:
                try:

                    cmd = (
                        "$(which git) clone -q --depth 1 "
                        + '--recurse-submodules --shallow-submodules %s "%s"'
                        % (self.task.processing_url, str(self.temp_path))
                    )

                    Cmd(
                        task=self.task,
                        run_id=self.run_id,
                        cmd=cmd,
                        success_msg="Repo cloned",
                        error_msg="Failed to clone repo: %s"
                        % (self.task.processing_url,),
                    ).shell()

                    processing_script_name = str(self.temp_path) + (
                        self.task.processing_command
                        if self.task.processing_command is not None
                        else ""
                    )
                # pylint: disable=broad-except
                except BaseException:
                    raise RunnerException(
                        self.task, self.run_id, 8, "Processor failed to clone repo."
                    )
            else:
                my_file = self.source_loader.web_url(self.task.processing_url)

        elif (
            self.task.processing_type_id == 6 and self.task.processing_code is not None
        ):
            my_file = self.task.processing_code
        elif self.task.processing_type_id > 0:
            raise RunnerException(
                self.task,
                self.run_id,
                8,
                "Processing error, Not enough information to run a processing script from.",
            )

        try:
            if my_file != "" and self.task.processing_type_id > 0:
                Path(processing_script_name).parent.mkdir(parents=True, exist_ok=True)
                with open(processing_script_name, "w") as text_file:
                    text_file.write(my_file)
                RunnerLog(self.task, self.run_id, 8, "Processing script created.")

        # pylint: disable=broad-except
        except BaseException as e:
            raise RunnerException(
                self.task, self.run_id, 8, f"Processing script failure:\n{e}"
            )

        # run processing script
        output = PyProcesser(
            task=self.task,
            run_id=self.run_id,
            directory=self.temp_path,
            source_files=self.source_files,
            script=self.task.processing_command or processing_script_name.name,
        ).run()

        # # allow processer to rename file
        if output:
            RunnerLog(self.task, self.run_id, 8, f"Processing script output:\n{output}")
            self.data_files = output

    def __store_files(self) -> None:
        if not self.source_files or len(self.source_files) == 0:
            return

        RunnerLog(
            self.task,
            self.run_id,
            8,
            "Storing output file%s..." % ("s" if len(self.source_files) != 1 else ""),
        )

        for file_counter, this_file in enumerate(self.source_files, 1):

            this_file_size = (
                self.query_output_size
                if self.query_output_size is not None
                else Path(this_file.name).stat().st_size
            )

            # get file name. if no name specified in task setting, then use temp name.
            try:
                file_name, file_path, file_hash = File(
                    task=self.task,
                    run_id=self.run_id,
                    data_file=this_file,
                    params=self.param_loader,
                ).save()

            except BaseException as e:
                raise RunnerException(
                    self.task, self.run_id, 11, f"Failed to create data file.\n{e}"
                )

            self.output_files.append(file_path)

            if len(self.source_files) > 1:
                RunnerLog(
                    self.task,
                    self.run_id,
                    8,
                    f"Storing file {file_counter} of {len(self.source_files)}...",
                )
            # store
            # send to sftp
            if self.task.destination_sftp == 1 and self.task.destination_sftp_conn:
                if (
                    self.task.destination_sftp_dont_send_empty_file == 1
                    and this_file_size == 0
                ):
                    RunnerLog(
                        self.task,
                        self.run_id,
                        8,
                        f"Skipping SFTP, file is empty.",
                    )
                else:
                    Sftp(
                        task=self.task,
                        run_id=self.run_id,
                        connection=self.task.destination_sftp_conn,
                        directory=self.temp_path,
                    ).save(
                        overwrite=self.task.destination_sftp_overwrite,
                        file_name=file_name,
                    )

            # send to ftp
            if self.task.destination_ftp == 1 and self.task.destination_ftp_conn:
                if (
                    self.task.destination_ftp_dont_send_empty_file == 1
                    and this_file_size == 0
                ):
                    RunnerLog(
                        self.task,
                        self.run_id,
                        8,
                        f"Skipping FTP, file is empty.",
                    )
                else:
                    Ftp(
                        task=self.task,
                        run_id=self.run_id,
                        connection=self.task.destination_ftp_conn,
                        directory=self.temp_path,
                    ).save(
                        overwrite=self.task.destination_ftp_overwrite,
                        file_name=file_name,
                    )

            # save to smb
            if self.task.destination_smb == 1 and self.task.destination_smb_conn:
                if (
                    self.task.destination_smb_dont_send_empty_file == 1
                    and this_file_size == 0
                ):
                    RunnerLog(
                        self.task,
                        self.run_id,
                        8,
                        f"Skipping SMB, file is empty.",
                    )
                else:
                    Smb(
                        task=self.task,
                        run_id=self.run_id,
                        connection=self.task.destination_smb_conn,
                        directory=self.temp_path,
                    ).save(
                        overwrite=self.task.destination_smb_overwrite,
                        file_name=file_name,
                    )

            # save historical copy
            smb_path = Smb(
                task=self.task,
                run_id=self.run_id,
                connection=None,  # "default",
                directory=self.temp_path,
            ).save(overwrite=1, file_name=file_name)

            # log file details
            db.session.add(
                TaskFile(
                    name=file_name,
                    path=smb_path,
                    task_id=self.task.id,
                    job_id=self.run_id,
                    file_hash=file_hash,
                    size=file_size(str(os.path.getsize(file_path))),
                )
            )
            db.session.commit()

    def __send_email(self) -> None:

        logs = (
            TaskLog.query.filter_by(task_id=self.task.id, job_id=self.run_id)
            .order_by(TaskLog.status_date.desc())  # type: ignore[union-attr]
            .all()
        )

        error_logs = (
            TaskLog.query.filter_by(task_id=self.task.id, job_id=self.run_id, error=1)
            .order_by(TaskLog.status_date)
            .all()
        )

        date = str(datetime.datetime.now())

        # pylint: disable=broad-except
        try:
            template = env.get_template("email/email.html.j2")
        except BaseException as e:
            raise RunnerException(
                self.task, self.run_id, 8, f"Failed to get email template.\n{e}"
            )

        # success email
        if self.task.email_completion == 1 and (
            (len(error_logs) < 1 and self.task.email_error == 1)
            or self.task.email_error != 1
        ):
            RunnerLog(self.task, self.run_id, 8, "Sending completion email.")

            output: List[List[str]] = []
            empty = 0
            attachments: List[str] = []

            if self.task.email_completion_file == 1 and len(self.output_files) > 0:
                for output_file in self.output_files:

                    if self.task.email_completion_file_embed == 1:
                        with open(output_file, newline="") as csvfile:
                            output.extend(list(csv.reader(csvfile)))

                    # check attachement file size if the task
                    # should not send blank files
                    if (
                        self.task.email_completion_dont_send_empty_file == 1
                        and output_file
                        # if query and data is blank, or other types and file is 0
                        and os.path.getsize(output_file) == 0
                    ):
                        empty = 1

                    attachments.append(output_file)

                if empty == 1:
                    RunnerLog(
                        self.task,
                        self.run_id,
                        8,
                        "Not sending completion email, file is empty.",
                    )
                    return

            Smtp(
                task=self.task,
                run_id=self.run_id,
                recipients=self.task.email_completion_recipients,
                subject="Project: %s / Task: %s / Run: %s %s"
                % (
                    self.task.project.name,
                    self.task.name,
                    self.run_id,
                    date,
                ),
                message=template.render(
                    task=self.task,
                    success=1,
                    date=date,
                    logs=logs,
                    output=output,
                    host=app.config["WEB_HOST"],
                ),
                short_message=self.task.email_completion_message
                or f"Atlas Hub job {self.task} completed successfully.",
                attachments=attachments,
            )

    def __clean_up(self) -> None:

        # remove file
        try:
            if Path(self.temp_path).exists():
                shutil.rmtree(self.temp_path)

        # pylint: disable=broad-except
        except BaseException as e:
            raise RunnerException(
                self.task, self.run_id, 8, f"Failed to clean up job.\n{e}"
            )
