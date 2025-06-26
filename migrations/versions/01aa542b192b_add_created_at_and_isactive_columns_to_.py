"""add created at and isactive columns  to users

Revision ID: 01aa542b192b
Revises: ca6ebdb4df40
Create Date: 2025-06-23 16:35:11.077425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01aa542b192b'
down_revision: Union[str, None] = 'ca6ebdb4df40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) add the new columns (both nullable for back-compat)
     
    op.add_column(
        "users",
        sa.Column("is_active", sa.String(), nullable=True),
    )
    # optional: index if you'll query by is_active a lot
    op.create_index("ix_users_is_active", "users", ["is_active"])


def downgrade() -> None:
    # reverse the changes
    # op.drop_index("ix_users_is_active", table_name="users")
    op.drop_column("users", "is_active")
     
