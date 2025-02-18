"""Python script runner."""


import re
from itertools import chain
from pathlib import Path
from typing import IO, List, Optional

from runner.model import Task
from runner.scripts.em_cmd import Cmd
from runner.scripts.em_messages import RunnerException


class PyProcesser:
    """Python Script Runner.

    Script will create a virtual environment, run a script or module, and then
    cleanup by removing all files.
    """

    def __init__(
        self,
        task: Task,
        run_id: str,
        directory: Path,
        script: str,
        source_files: List[IO[str]],
    ) -> None:
        """Set up class parameters."""
        self.task = task
        self.run_id = run_id
        self.script = script
        self.output = ""

        self.env_name = self.run_id + "_env"
        self.job_path = directory
        self.source_files = source_files
        self.base_path = str(self.job_path / "venv")

        Path(self.base_path).mkdir(parents=True, exist_ok=True)

        self.env_path = self.base_path  # + self.env_name

    def run(self) -> Optional[List[Path]]:
        """Run processing script.

        :returns: Any output from the script.
        """
        self.__build_env()
        self.__pip_install()
        self.__run_script()

        # if output is not a file list, then swallow it.

        if isinstance(self.output, List):
            return self.output
        return None

    def __build_env(self) -> None:
        """Build a virtual environment.

        Runs command:
        .. code-block:: console

            virtualenv <path>

        """
        try:
            Cmd(
                task=self.task,
                run_id=self.run_id,
                cmd=f'virtualenv "{self.env_path}"',
                success_msg=f"Environment created.\n{self.env_path}",
                error_msg=f"Failed to create environment.\n{self.env_path}",
            ).shell()

        # pylint: disable=broad-except
        except BaseException as e:
            raise RunnerException(
                self.task,
                self.run_id,
                14,
                f"Failed to build environment.\n{self.base_path}\n{e}",
            )

    def __pip_install(self) -> None:
        r"""Get includes from script.

        get import (...)
        (?<=^import)\s+[^\.][^\s]+?\\s+?$

        get import (...) as ...
        (?<=^import)\s+[^\.][^\s]+?(?=\s)

        get from (...) imoprt (...)
        (?<=^from)\s+[^\.].+?(?=import)
        """
        try:
            imports = []

            # find all scripts in dir, but not in venv
            paths = list(
                set(Path(self.job_path).rglob("*.py"))
                - set(Path(self.env_path).rglob("*.py"))
            )

            for this_file in paths:
                with open(this_file, "r") as my_file:
                    for line in my_file:

                        imports.extend(
                            re.findall(r"(?<=^import)\s+[^\.][^\s]+?\s+?$", line)
                        )
                        imports.extend(
                            re.findall(r"(?<=^from)\s+[^\.].+?(?=import)", line)
                        )
                        imports.extend(
                            re.findall(r"(?<=^import)\s+[^\.][^\s]+?(?=\s)", line)
                        )

            package_map = {"dateutil": "python-dateutil", "smb": "pysmb"}

            # clean list
            imports = [
                str(package_map.get(x.strip().split(".")[0], x.strip().split(".")[0]))
                for x in imports
                if x.strip() != ""
            ]

            # remove any relative imports
            names = [my_file.stem for my_file in paths]

            imports = list(set(imports) - set(names))

            # remove preinstalled packages from imports
            cmd = f'"{self.env_path}/bin/python" -c "help(\'modules\')"'
            built_in_packages = Cmd(
                task=self.task,
                run_id=self.run_id,
                cmd=cmd,
                success_msg="Python packages loaded.",
                error_msg="Failed to get preloaded packages: " + "\n" + cmd,
            ).shell()

            built_in_packages = built_in_packages.split(
                "Please wait a moment while I gather a list of all available modules..."
            )[1].split("Enter any module name to get more help.")[0]

            cleaned_built_in_packages = [
                this_out.strip()
                for this_out in list(
                    chain.from_iterable(
                        [g.split(" ") for g in built_in_packages.split("\n") if g != ""]
                    )
                )
                if this_out.strip() != ""
            ]

            # remove default python packages from list
            imports = [
                x.strip()
                for x in imports
                if x not in cleaned_built_in_packages and x.strip()
            ]

            # try to install
            if len(imports) > 0:
                cmd = (
                    f'"{self.env_path}/bin/pip" install --disable-pip-version-check --quiet '
                    + " ".join([str(x) for x in imports])
                )
                Cmd(
                    task=self.task,
                    run_id=self.run_id,
                    cmd=cmd,
                    success_msg="Imports succesfully installed: "
                    + ", ".join([str(x) for x in imports])
                    + " with command: "
                    + "\n"
                    + cmd,
                    error_msg="Failed to install imports with command: " + "\n" + cmd,
                ).shell()

        except BaseException as e:
            raise RunnerException(
                self.task,
                self.run_id,
                14,
                f"Failed to install packages.\n{self.base_path}\n{e}",
            )

    def __run_script(self) -> None:
        try:
            # if data files exist, pass them as a param.
            cmd = (
                f'"{self.env_path}/bin/python" "{self.job_path}/{self.script}" '
            ) + " ".join([f'"{x.name}"' for x in self.source_files])

            self.output = Cmd(
                task=self.task,
                run_id=self.run_id,
                cmd=cmd,
                success_msg="Script successfully run.",
                error_msg="Failed run script: " + "\n" + cmd,
            ).shell()

        except BaseException as e:
            raise RunnerException(
                self.task,
                self.run_id,
                14,
                f"Failed to build run script.\n{self.base_path}\n{e}",
            )
