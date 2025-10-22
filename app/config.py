import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENV: str = "development"  # "production" or "development"

    # Local & Production Databases
    DATABASE_URL_DEV: str = "postgresql://postgres:ngharry00@db.qvucveskwcpcssrinszg.supabase.co:5432/postgres"
    DATABASE_URL_PROD: str = "postgresql://postgres:jnmkl,hghfdfghjs"

    # JWT
    SECRET_KEY: str = "super-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    PROJECT_NAME: str = "BookIt API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self) -> str:
        """
        Return local DB in development and production DB in production mode.
        """
        if self.ENV.lower() == "production":
            return self.DATABASE_URL_PROD
        return self.DATABASE_URL_DEV


settings = Settings()
