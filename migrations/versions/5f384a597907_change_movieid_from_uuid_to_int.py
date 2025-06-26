"""change movieId from UUID TO int

Revision ID: 5f384a597907
Revises: ef15796f3e7e
Create Date: 2025-06-12 23:59:44.245546

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f384a597907'
down_revision: Union[str, None] = 'ef15796f3e7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
INT  = sa.Integer

def _drop_fk_if_exists(table, name):
    # helper to tolerate whatever FK name exists
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = '{name}'
                  AND conrelid = '{table}'::regclass
            ) THEN
                ALTER TABLE {table} DROP CONSTRAINT {name};
            END IF;
        END $$;
        """
    )

def upgrade() -> None:
    # 0) optional: create integer sequence for movies PK
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS movies_movie_id_seq
        OWNED BY movies.movie_id;
        """
    )

    # 1) drop FK from ratings → movies (could be fk_movie OR fk_ratings_movie_id_movies)
    _drop_fk_if_exists("ratings", "fk_movie")
    _drop_fk_if_exists("ratings", "fk_ratings_movie_id_movies")

    # 2) ratings.movie_id UUID → INT
    with op.batch_alter_table("ratings") as batch:
        batch.alter_column(
            "movie_id",
            existing_type=UUID,
            type_=INT,
            postgresql_using="movie_id::text::uuid::text::integer",
            nullable=False,
        )

    # 3) movies.movie_id UUID → INT
    # 3a) drop the existing default (uuid_generate_v4)
    op.execute("ALTER TABLE movies ALTER COLUMN movie_id DROP DEFAULT;")

    # 3b) change the column type
    op.execute(
        """
        ALTER TABLE movies
        ALTER COLUMN movie_id
        TYPE INTEGER
        USING movie_id::text::uuid::text::integer;
        """
    )

    # 3c) (optional) attach an integer sequence as new default
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS movies_movie_id_seq OWNED BY movies.movie_id;
        ALTER TABLE movies ALTER COLUMN movie_id
        SET DEFAULT nextval('movies_movie_id_seq');
        """
    )

    # 4) recreate FK
    with op.batch_alter_table("ratings") as batch:
        batch.create_foreign_key(
            "fk_ratings_movie_id_movies",
            "movies",
            ["movie_id"],
            ["movie_id"],
            ondelete="CASCADE",
        )