"""empty message

Revision ID: 78a9731d2953
Revises: 88d238f430da
Create Date: 2021-04-19 15:32:43.712143

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78a9731d2953"
down_revision = "88d238f430da"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("first_name", sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "first_name")
    # ### end Alembic commands ###
