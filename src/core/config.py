from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    PROJECT_NAME: str = "Movie Recommender"
    JWT_ALGORITHM: str = "HS256"
    DATABASE_URI: str
    JWT_SECRET_KEY: str
    TMDB_API_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"  # Tells Pydantic to load from .env

settings = Settings()
