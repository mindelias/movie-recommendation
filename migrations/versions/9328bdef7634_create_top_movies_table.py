"""Create top_movies table

Revision ID: 9328bdef7634
Revises: 564eafb37bb9
Create Date: 2025-04-03 11:24:23.651070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9328bdef7634'
down_revision: Union[str, None] = '564eafb37bb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'top_movies',
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('mean_rating', sa.Float(), nullable=False),
        sa.Column('rating_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('movie_id'),
    )
    op.create_index(op.f('ix_top_movies_movie_id'), 'top_movies', ['movie_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_top_movies_movie_id'), table_name='top_movies')
    op.drop_table('top_movies')
