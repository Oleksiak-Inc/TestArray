import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    ENV_FILE = BASE_DIR.parent / ".env"
else:
    ENV_FILE = BASE_DIR.parent / f".env.{ENVIRONMENT}"
load_dotenv(ENV_FILE)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "TestArray"

    API_V1_STR: str

    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 12

    SERVER_HOST: str
    SERVER_PORT: int

    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: Optional[AnyUrl] = None

    FRONTEND_ORIGINS: str

    UPLOAD_DIR: str

    MAX_FILE_SIZE: int = 100 * (1024 ** 2)
    ALLOWED_FILE_EXTENSIONS: set = {
        ".txt",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".csv",
        ".json",
        ".xml",
    }

settings = Settings()