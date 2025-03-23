"""Rename user_id to id

Revision ID: 6a11599bbe44
Revises: 
Create Date: 2025-03-23 16:05:05.533629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a11599bbe44'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'user_id', new_column_name='id')

def downgrade():
    op.alter_column('users', 'id', new_column_name='user_id')