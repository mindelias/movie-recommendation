"""Fix primary key generation for User

Revision ID: 564eafb37bb9
Revises: 6a11599bbe44
Create Date: 2025-03-23 16:56:51.987525
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '564eafb37bb9'
down_revision: Union[str, None] = '6a11599bbe44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1) Ensure the extension is installed (requires superuser or the necessary privilege).
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # 2) If your 'id' column is already UUID but missing a default:
    op.alter_column(
        'users',
        'id',
        server_default=sa.text("uuid_generate_v4()")
    )

    # If the column is NOT already UUID, but is INT or something else,
    # you need to convert it:
    #
    # op.alter_column(
    #     'users',
    #     'id',
    #     type_=postgresql.UUID,
    #     server_default=sa.text("uuid_generate_v4()"),
    #     existing_type=sa.Integer(),  # or whatever the old type is
    #     postgresql_using="id::uuid"
    # )

def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the default setting if you want to be thorough.
    op.alter_column(
        'users',
        'id',
        server_default=None
    )

    # Optionally remove the extension. Usually, you might leave it alone:
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
