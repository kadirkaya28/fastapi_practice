"""add content column to posts table

Revision ID: 191e75267222
Revises: 1c3e2dac8605
Create Date: 2022-11-15 10:13:40.908268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '191e75267222'
down_revision = '1c3e2dac8605'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
