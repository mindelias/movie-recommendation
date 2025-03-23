from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Create the engine for PostgreSQL using the URI from settings
engine = create_engine(
    settings.DATABASE_URI,
    # No connect_args for Postgres in most cases
    # echo=True  # Uncomment this if you want to log all SQL queries
)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
