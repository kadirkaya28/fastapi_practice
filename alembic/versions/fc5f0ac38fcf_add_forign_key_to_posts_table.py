"""add forign key to posts table

Revision ID: fc5f0ac38fcf
Revises: cf38b37ffea0
Create Date: 2022-11-15 10:41:19.148002

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fc5f0ac38fcf'
down_revision = 'cf38b37ffea0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key("post_user_fk", referent_table="users",
                                    local_cols=["owner_id"],
                                    remote_cols=["id"], ondelete="CASCADE")


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:

        batch_op.drop_constraint("post_user_fk")
        batch_op.drop_column("owner_id")
