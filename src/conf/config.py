from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://POSTGRES_USER:POSTGRES_PASSWORD@POSTGRES_DOMAIN:5432/POSTGRES_DB"
    SECRET_KEY_JWT: str = "secret_jwt"
    ALGORITHM: str = "HS256"
    
    MAIL_USERNAME: EmailStr = "postgres@meail.com"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "postgres"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "postgres"

    CLOUDINARY_NAME: str = "cloudinary_name"
    CLOUDINARY_API_KEY: int = 0000000000000
    CLOUDINARY_API_SECRET: str = "cloudinary_api_secret"

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
