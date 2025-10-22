import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Force load .env file
load_dotenv()

class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "development")  # "production" or "development"

    # Databases
    DATABASE_URL_DEV: str = os.getenv("DATABASE_URL_DEV", "sqlite+aiosqlite:///./bookit.db")
    DATABASE_URL_PROD: str = os.getenv("DATABASE_URL_PROD", "postgresql://postgres:your-production-password@your-production-host:5432/your-database")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-12345")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # App
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "BookIt API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def DATABASE_URL(self) -> str:
        """
        Return SQLite in development and PostgreSQL in production mode.
        """
        if self.ENV.lower() == "production":
            print("Using PRODUCTION database (PostgreSQL)")
            return self.DATABASE_URL_PROD
        else:
            print("Using DEVELOPMENT database (SQLite)")
            return self.DATABASE_URL_DEV


settings = Settings()

# Debug output
print(f"Environment: {settings.ENV}")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Database Type: {'PostgreSQL' if settings.ENV == 'production' else 'SQLite'}")
print(f"Project: {settings.PROJECT_NAME} v{settings.VERSION}")