"""Reduce size of OAuthAccount.account_id and OAuthAccount.account_email for MySQL compat

Revision ID: ab9cf21c76dd
Revises: aa662768d69b
Create Date: 2022-11-29 10:10:43.160013

"""
import sqlalchemy as sa
from alembic import op

import fief

# revision identifiers, used by Alembic.
revision = "ab9cf21c76dd"
down_revision = "aa662768d69b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    if connection.dialect.name == "sqlite":
        with op.batch_alter_table("fief_oauth_accounts") as batch_op:
            batch_op.alter_column(
                "account_id",
                type_=sa.String(512),
                existing_type=sa.String(1024),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "account_email",
                type_=sa.String(512),
                existing_type=sa.String(1024),
                existing_nullable=False,
            )
    else:
        op.alter_column(
            "fief_oauth_accounts",
            "account_id",
            type_=sa.String(512),
            existing_type=sa.String(1024),
            existing_nullable=False,
        )
        op.alter_column(
            "fief_oauth_accounts",
            "account_email",
            type_=sa.String(512),
            existing_type=sa.String(1024),
            existing_nullable=True,
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
