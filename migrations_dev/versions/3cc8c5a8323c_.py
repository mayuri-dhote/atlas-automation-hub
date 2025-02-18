"""empty message

Revision ID: 3cc8c5a8323c
Revises: 
Create Date: 2021-01-11 15:57:03.017512

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3cc8c5a8323c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "connection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=120), nullable=True),
        sa.Column("address", sa.String(length=120), nullable=True),
        sa.Column("primary_contact", sa.String(length=400), nullable=True),
        sa.Column("primary_contact_email", sa.String(length=120), nullable=True),
        sa.Column("primary_contact_phone", sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_connection_id"), "connection", ["id"], unique=False)
    op.create_table(
        "connection_database_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "login_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_login_type_id"), "login_type", ["id"], unique=False)
    op.create_table(
        "quote_level",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quote_level_id"), "quote_level", ["id"], unique=False)
    op.create_table(
        "task_destination_file_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("ext", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task_processing_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task_source_query_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task_source_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "task_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_user_user_id"), "user", ["user_id"], unique=False)
    op.create_table(
        "connection_database",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("connection_string", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connection.id"],
        ),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["connection_database_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connection_database_connection_id"),
        "connection_database",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connection_database_id"), "connection_database", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_connection_database_type_id"),
        "connection_database",
        ["type_id"],
        unique=False,
    )
    op.create_table(
        "connection_ftp",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("username", sa.String(length=500), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connection.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connection_ftp_connection_id"),
        "connection_ftp",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connection_ftp_id"), "connection_ftp", ["id"], unique=False
    )
    op.create_table(
        "connection_sftp",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connection.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connection_sftp_connection_id"),
        "connection_sftp",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connection_sftp_id"), "connection_sftp", ["id"], unique=False
    )
    op.create_table(
        "connection_smb",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("share_name", sa.String(length=500), nullable=False),
        sa.Column("path", sa.String(length=1000), nullable=False),
        sa.Column("username", sa.String(length=500), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("server_ip", sa.String(length=500), nullable=False),
        sa.Column("server_name", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connection.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connection_smb_connection_id"),
        "connection_smb",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connection_smb_id"), "connection_smb", ["id"], unique=False
    )
    op.create_table(
        "connection_ssh",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["connection.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connection_ssh_connection_id"),
        "connection_ssh",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connection_ssh_id"), "connection_ssh", ["id"], unique=False
    )
    op.create_table(
        "login",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column(
            "login_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["login_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_login_id"), "login", ["id"], unique=False)
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("description", sa.String(length=8000), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("cron", sa.Integer(), nullable=True),
        sa.Column("cron_year", sa.Integer(), nullable=True),
        sa.Column("cron_month", sa.Integer(), nullable=True),
        sa.Column("cron_week", sa.Integer(), nullable=True),
        sa.Column("cron_day", sa.Integer(), nullable=True),
        sa.Column("cron_week_day", sa.Integer(), nullable=True),
        sa.Column("cron_hour", sa.Integer(), nullable=True),
        sa.Column("cron_min", sa.Integer(), nullable=True),
        sa.Column("cron_sec", sa.Integer(), nullable=True),
        sa.Column("cron_start_date", sa.DateTime(), nullable=True),
        sa.Column("cron_end_date", sa.DateTime(), nullable=True),
        sa.Column("intv", sa.Integer(), nullable=True),
        sa.Column("intv_type", sa.String(length=5), nullable=True),
        sa.Column("intv_value", sa.Integer(), nullable=True),
        sa.Column("intv_start_date", sa.DateTime(), nullable=True),
        sa.Column("intv_end_date", sa.DateTime(), nullable=True),
        sa.Column("ooff", sa.Integer(), nullable=True),
        sa.Column("ooff_date", sa.DateTime(), nullable=True),
        sa.Column("global_params", sa.String(length=8000), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("creator_id", sa.Integer(), nullable=True),
        sa.Column("updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updater_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updater_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_project_creator_id"), "project", ["creator_id"], unique=False
    )
    op.create_index(op.f("ix_project_id"), "project", ["id"], unique=False)
    op.create_index(op.f("ix_project_owner_id"), "project", ["owner_id"], unique=False)
    op.create_index(
        op.f("ix_project_updater_id"), "project", ["updater_id"], unique=False
    )
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=1000), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("status_id", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Integer(), nullable=True),
        sa.Column("last_run", sa.DateTime(), nullable=True),
        sa.Column("last_run_job_id", sa.String(length=30), nullable=True),
        sa.Column("next_run", sa.DateTime(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("creator_id", sa.Integer(), nullable=True),
        sa.Column("updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updater_id", sa.Integer(), nullable=True),
        sa.Column("source_type_id", sa.Integer(), nullable=True),
        sa.Column("source_query_type_id", sa.Integer(), nullable=True),
        sa.Column("source_query_include_header", sa.Integer(), nullable=True),
        sa.Column("source_git", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("source_code", sa.String(length=8000), nullable=True),
        sa.Column("query_smb_id", sa.Integer(), nullable=True),
        sa.Column("query_smb_file", sa.String(length=1000), nullable=True),
        sa.Column("query_sftp_id", sa.Integer(), nullable=True),
        sa.Column("query_sftp_file", sa.String(length=1000), nullable=True),
        sa.Column("query_ftp_id", sa.Integer(), nullable=True),
        sa.Column("query_ftp_file", sa.String(length=1000), nullable=True),
        sa.Column("query_params", sa.String(length=8000), nullable=True),
        sa.Column("source_smb_file", sa.String(length=1000), nullable=True),
        sa.Column("source_smb_delimiter", sa.String(length=10), nullable=True),
        sa.Column("source_smb_ignore_delimiter", sa.Integer(), nullable=True),
        sa.Column("source_smb_id", sa.Integer(), nullable=True),
        sa.Column("source_ftp_file", sa.String(length=1000), nullable=True),
        sa.Column("source_ftp_delimiter", sa.String(length=10), nullable=True),
        sa.Column("source_ftp_ignore_delimiter", sa.Integer(), nullable=True),
        sa.Column("source_ftp_id", sa.Integer(), nullable=True),
        sa.Column("source_sftp_file", sa.String(length=1000), nullable=True),
        sa.Column("source_sftp_delimiter", sa.String(length=10), nullable=True),
        sa.Column("source_sftp_ignore_delimiter", sa.Integer(), nullable=True),
        sa.Column("source_sftp_id", sa.Integer(), nullable=True),
        sa.Column("source_database_id", sa.Integer(), nullable=True),
        sa.Column("source_ssh_id", sa.Integer(), nullable=True),
        sa.Column("processing_type_id", sa.Integer(), nullable=True),
        sa.Column("processing_smb_id", sa.Integer(), nullable=True),
        sa.Column("processing_smb_file", sa.String(length=1000), nullable=True),
        sa.Column("processing_sftp_id", sa.Integer(), nullable=True),
        sa.Column("processing_sftp_file", sa.String(length=1000), nullable=True),
        sa.Column("processing_ftp_id", sa.Integer(), nullable=True),
        sa.Column("processing_ftp_file", sa.String(length=1000), nullable=True),
        sa.Column("processing_code", sa.String(length=8000), nullable=True),
        sa.Column("processing_url", sa.String(length=1000), nullable=True),
        sa.Column("processing_git", sa.String(length=1000), nullable=True),
        sa.Column("processing_command", sa.String(length=1000), nullable=True),
        sa.Column("destination_file_name", sa.String(length=1000), nullable=True),
        sa.Column("destination_file_delimiter", sa.String(length=10), nullable=True),
        sa.Column("destination_ignore_delimiter", sa.Integer(), nullable=True),
        sa.Column("destination_create_zip", sa.Integer(), nullable=True),
        sa.Column("destination_zip_name", sa.String(length=1000), nullable=True),
        sa.Column("destination_file_type_id", sa.Integer(), nullable=True),
        sa.Column("destination_sftp", sa.Integer(), nullable=True),
        sa.Column("destination_sftp_overwrite", sa.Integer(), nullable=True),
        sa.Column("destination_sftp_id", sa.Integer(), nullable=True),
        sa.Column("destination_ftp", sa.Integer(), nullable=True),
        sa.Column("destination_ftp_overwrite", sa.Integer(), nullable=True),
        sa.Column("destination_ftp_id", sa.Integer(), nullable=True),
        sa.Column("destination_smb", sa.Integer(), nullable=True),
        sa.Column("destination_smb_overwrite", sa.Integer(), nullable=True),
        sa.Column("destination_smb_id", sa.Integer(), nullable=True),
        sa.Column("destination_quote_level_id", sa.Integer(), nullable=True),
        sa.Column("email_completion", sa.Integer(), nullable=True),
        sa.Column("email_completion_log", sa.Integer(), nullable=True),
        sa.Column("email_completion_file", sa.Integer(), nullable=True),
        sa.Column("email_completion_recipients", sa.String(length=1000), nullable=True),
        sa.Column("email_completion_message", sa.String(length=8000), nullable=True),
        sa.Column("email_completion_dont_send_empty_file", sa.Integer(), nullable=True),
        sa.Column("email_error", sa.Integer(), nullable=True),
        sa.Column("email_error_recipients", sa.String(length=1000), nullable=True),
        sa.Column("email_error_message", sa.String(length=8000), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_file_type_id"],
            ["task_destination_file_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_ftp_id"],
            ["connection_ftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_quote_level_id"],
            ["quote_level.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_sftp_id"],
            ["connection_sftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_smb_id"],
            ["connection_smb.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processing_ftp_id"],
            ["connection_ftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processing_sftp_id"],
            ["connection_sftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processing_smb_id"],
            ["connection_smb.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processing_type_id"],
            ["task_processing_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["query_ftp_id"],
            ["connection_ftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["query_sftp_id"],
            ["connection_sftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["query_smb_id"],
            ["connection_smb.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_database_id"],
            ["connection_database.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_ftp_id"],
            ["connection_ftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_query_type_id"],
            ["task_source_query_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_sftp_id"],
            ["connection_sftp.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_smb_id"],
            ["connection_smb.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_ssh_id"],
            ["connection_ssh.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_type_id"],
            ["task_source_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["task_status.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updater_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_created"), "task", ["created"], unique=False)
    op.create_index(op.f("ix_task_creator_id"), "task", ["creator_id"], unique=False)
    op.create_index(
        op.f("ix_task_destination_file_type_id"),
        "task",
        ["destination_file_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_destination_ftp"), "task", ["destination_ftp"], unique=False
    )
    op.create_index(
        op.f("ix_task_destination_ftp_id"), "task", ["destination_ftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_destination_quote_level_id"),
        "task",
        ["destination_quote_level_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_destination_sftp"), "task", ["destination_sftp"], unique=False
    )
    op.create_index(
        op.f("ix_task_destination_sftp_id"),
        "task",
        ["destination_sftp_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_destination_smb"), "task", ["destination_smb"], unique=False
    )
    op.create_index(
        op.f("ix_task_destination_smb_id"), "task", ["destination_smb_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_email_completion"), "task", ["email_completion"], unique=False
    )
    op.create_index(op.f("ix_task_email_error"), "task", ["email_error"], unique=False)
    op.create_index(op.f("ix_task_enabled"), "task", ["enabled"], unique=False)
    op.create_index(op.f("ix_task_id"), "task", ["id"], unique=False)
    op.create_index(
        op.f("ix_task_last_run_job_id"), "task", ["last_run_job_id"], unique=False
    )
    op.create_index(op.f("ix_task_next_run"), "task", ["next_run"], unique=False)
    op.create_index(
        op.f("ix_task_processing_ftp_id"), "task", ["processing_ftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_processing_sftp_id"), "task", ["processing_sftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_processing_smb_id"), "task", ["processing_smb_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_processing_type_id"), "task", ["processing_type_id"], unique=False
    )
    op.create_index(op.f("ix_task_project_id"), "task", ["project_id"], unique=False)
    op.create_index(
        op.f("ix_task_query_ftp_id"), "task", ["query_ftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_query_sftp_id"), "task", ["query_sftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_query_smb_id"), "task", ["query_smb_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_database_id"), "task", ["source_database_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_ftp_id"), "task", ["source_ftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_query_type_id"),
        "task",
        ["source_query_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_source_sftp_id"), "task", ["source_sftp_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_smb_id"), "task", ["source_smb_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_ssh_id"), "task", ["source_ssh_id"], unique=False
    )
    op.create_index(
        op.f("ix_task_source_type_id"), "task", ["source_type_id"], unique=False
    )
    op.create_index(op.f("ix_task_status_id"), "task", ["status_id"], unique=False)
    op.create_index(op.f("ix_task_updated"), "task", ["updated"], unique=False)
    op.create_index(op.f("ix_task_updater_id"), "task", ["updater_id"], unique=False)
    op.create_table(
        "task_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=1000), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.String(length=1000), nullable=True),
        sa.Column("size", sa.String(length=200), nullable=True),
        sa.Column("path", sa.String(length=1000), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["task.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_task_file_created"), "task_file", ["created"], unique=False
    )
    op.create_index(op.f("ix_task_file_id"), "task_file", ["id"], unique=False)
    op.create_index(
        "ix_task_file_id_task_id_job_id",
        "task_file",
        ["id", "task_id", "job_id"],
        unique=False,
    )
    op.create_index(op.f("ix_task_file_job_id"), "task_file", ["job_id"], unique=False)
    op.create_index(op.f("ix_task_file_name"), "task_file", ["name"], unique=False)
    op.create_index(op.f("ix_task_file_path"), "task_file", ["path"], unique=False)
    op.create_index(op.f("ix_task_file_size"), "task_file", ["size"], unique=False)
    op.create_index(
        op.f("ix_task_file_task_id"), "task_file", ["task_id"], unique=False
    )
    op.create_table(
        "task_log",
        sa.Column("job_id", sa.String(length=1000), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("status_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status_date", sa.DateTime(), nullable=True),
        sa.Column("error", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["task_status.id"],
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["task.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_log_error"), "task_log", ["error"], unique=False)
    op.create_index(op.f("ix_task_log_id"), "task_log", ["id"], unique=False)
    op.create_index(op.f("ix_task_log_job_id"), "task_log", ["job_id"], unique=False)
    op.create_index(
        op.f("ix_task_log_status_date"), "task_log", ["status_date"], unique=False
    )
    op.create_index(
        "ix_task_log_status_date_error",
        "task_log",
        ["status_date", "error"],
        unique=False,
    )
    op.create_index(
        op.f("ix_task_log_status_id"), "task_log", ["status_id"], unique=False
    )
    op.create_index(op.f("ix_task_log_task_id"), "task_log", ["task_id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_task_log_task_id"), table_name="task_log")
    op.drop_index(op.f("ix_task_log_status_id"), table_name="task_log")
    op.drop_index("ix_task_log_status_date_error", table_name="task_log")
    op.drop_index(op.f("ix_task_log_status_date"), table_name="task_log")
    op.drop_index(op.f("ix_task_log_job_id"), table_name="task_log")
    op.drop_index(op.f("ix_task_log_id"), table_name="task_log")
    op.drop_index(op.f("ix_task_log_error"), table_name="task_log")
    op.drop_table("task_log")
    op.drop_index(op.f("ix_task_file_task_id"), table_name="task_file")
    op.drop_index(op.f("ix_task_file_size"), table_name="task_file")
    op.drop_index(op.f("ix_task_file_path"), table_name="task_file")
    op.drop_index(op.f("ix_task_file_name"), table_name="task_file")
    op.drop_index(op.f("ix_task_file_job_id"), table_name="task_file")
    op.drop_index("ix_task_file_id_task_id_job_id", table_name="task_file")
    op.drop_index(op.f("ix_task_file_id"), table_name="task_file")
    op.drop_index(op.f("ix_task_file_created"), table_name="task_file")
    op.drop_table("task_file")
    op.drop_index(op.f("ix_task_updater_id"), table_name="task")
    op.drop_index(op.f("ix_task_updated"), table_name="task")
    op.drop_index(op.f("ix_task_status_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_type_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_ssh_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_smb_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_sftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_query_type_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_ftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_source_database_id"), table_name="task")
    op.drop_index(op.f("ix_task_query_smb_id"), table_name="task")
    op.drop_index(op.f("ix_task_query_sftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_query_ftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_project_id"), table_name="task")
    op.drop_index(op.f("ix_task_processing_type_id"), table_name="task")
    op.drop_index(op.f("ix_task_processing_smb_id"), table_name="task")
    op.drop_index(op.f("ix_task_processing_sftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_processing_ftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_next_run"), table_name="task")
    op.drop_index(op.f("ix_task_last_run_job_id"), table_name="task")
    op.drop_index(op.f("ix_task_id"), table_name="task")
    op.drop_index(op.f("ix_task_enabled"), table_name="task")
    op.drop_index(op.f("ix_task_email_error"), table_name="task")
    op.drop_index(op.f("ix_task_email_completion"), table_name="task")
    op.drop_index(op.f("ix_task_destination_smb_id"), table_name="task")
    op.drop_index(op.f("ix_task_destination_smb"), table_name="task")
    op.drop_index(op.f("ix_task_destination_sftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_destination_sftp"), table_name="task")
    op.drop_index(op.f("ix_task_destination_quote_level_id"), table_name="task")
    op.drop_index(op.f("ix_task_destination_ftp_id"), table_name="task")
    op.drop_index(op.f("ix_task_destination_ftp"), table_name="task")
    op.drop_index(op.f("ix_task_destination_file_type_id"), table_name="task")
    op.drop_index(op.f("ix_task_creator_id"), table_name="task")
    op.drop_index(op.f("ix_task_created"), table_name="task")
    op.drop_table("task")
    op.drop_index(op.f("ix_project_updater_id"), table_name="project")
    op.drop_index(op.f("ix_project_owner_id"), table_name="project")
    op.drop_index(op.f("ix_project_id"), table_name="project")
    op.drop_index(op.f("ix_project_creator_id"), table_name="project")
    op.drop_table("project")
    op.drop_index(op.f("ix_login_id"), table_name="login")
    op.drop_table("login")
    op.drop_index(op.f("ix_connection_ssh_id"), table_name="connection_ssh")
    op.drop_index(op.f("ix_connection_ssh_connection_id"), table_name="connection_ssh")
    op.drop_table("connection_ssh")
    op.drop_index(op.f("ix_connection_smb_id"), table_name="connection_smb")
    op.drop_index(op.f("ix_connection_smb_connection_id"), table_name="connection_smb")
    op.drop_table("connection_smb")
    op.drop_index(op.f("ix_connection_sftp_id"), table_name="connection_sftp")
    op.drop_index(
        op.f("ix_connection_sftp_connection_id"), table_name="connection_sftp"
    )
    op.drop_table("connection_sftp")
    op.drop_index(op.f("ix_connection_ftp_id"), table_name="connection_ftp")
    op.drop_index(op.f("ix_connection_ftp_connection_id"), table_name="connection_ftp")
    op.drop_table("connection_ftp")
    op.drop_index(
        op.f("ix_connection_database_type_id"), table_name="connection_database"
    )
    op.drop_index(op.f("ix_connection_database_id"), table_name="connection_database")
    op.drop_index(
        op.f("ix_connection_database_connection_id"), table_name="connection_database"
    )
    op.drop_table("connection_database")
    op.drop_index(op.f("ix_user_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")
    op.drop_table("task_status")
    op.drop_table("task_source_type")
    op.drop_table("task_source_query_type")
    op.drop_table("task_processing_type")
    op.drop_table("task_destination_file_type")
    op.drop_index(op.f("ix_quote_level_id"), table_name="quote_level")
    op.drop_table("quote_level")
    op.drop_index(op.f("ix_login_type_id"), table_name="login_type")
    op.drop_table("login_type")
    op.drop_table("connection_database_type")
    op.drop_index(op.f("ix_connection_id"), table_name="connection")
    op.drop_table("connection")
    # ### end Alembic commands ###
