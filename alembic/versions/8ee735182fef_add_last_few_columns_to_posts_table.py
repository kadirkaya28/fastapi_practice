"""add last few columns to posts table

Revision ID: 8ee735182fef
Revises: fc5f0ac38fcf
Create Date: 2022-11-15 11:30:25.863654

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = '8ee735182fef'
down_revision = 'fc5f0ac38fcf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("published", sa.Boolean(), nullable=False, server_default=expression.true()))
    op.add_column("posts", sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                                     server_default=sa.text("(datetime('now', 'localtime'))"), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
