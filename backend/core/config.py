from pathlib import Path
from typing import Optional
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "TestArray"
    API_V1_STR: str = Field(..., env="API_V1_STR")

    #SECRET_KEY: str = Field(..., env="SECRET_KEY")
    #JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 12
    
    SERVER_HOST: str = Field(..., env="SERVER_HOST")
    SERVER_PORT: int = Field(..., env="SERVER_PORT")

    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    DATABASE_URL: Optional[PostgresDsn] = None
    POSTGRES_PORT: str = Field(..., env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")

    FRONTEND_ORIGINS: str = Field(..., env="FRONTEND_ORIGINS")
    #JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")

    UPLOAD_DIR: str = Field(..., env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024
    ALLOWED_FILE_EXTENSIONS: set = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.csv', '.json', '.xml'}

    @property
    def get_upload_path(self) -> Path:
        upload_path = Path(self.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path
    
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return str(self.DATABASE_URL)
        return str(PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT) if self.POSTGRES_PORT else None,
            path=self.POSTGRES_DB or None,
        ))

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()