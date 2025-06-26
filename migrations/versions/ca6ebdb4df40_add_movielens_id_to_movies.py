"""add movielens_id to movies

Revision ID: ca6ebdb4df40
Revises: 5f384a597907
Create Date: 2025-06-23 14:27:40.050729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca6ebdb4df40'
down_revision: Union[str, None] = '5f384a597907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass


def upgrade():
    op.add_column("movies", sa.Column("movielens_id", sa.Integer(), nullable=True))
    op.create_index("ix_movies_movielens_id", "movies", ["movielens_id"], unique=True)

def downgrade():
    op.drop_index("ix_movies_movielens_id", table_name="movies")
    op.drop_column("movies", "movielens_id")
