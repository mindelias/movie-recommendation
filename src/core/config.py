from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    PROJECT_NAME: str = "Movie Recommender"
    JWT_ALGORITHM: str = "HS256"
    DATABASE_URI: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"  # Tells Pydantic to load from .env

settings = Settings()
