import os
print("DEBUG DATABASE_URL:", os.getenv("DATABASE_URL", "NOT FOUND"))

from pydantic_settings import BaseSettings
from databases import Database
from sqlalchemy import create_engine, MetaData

class Settings(BaseSettings):
    database_url: str
    secret_key: str = "fallback"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    frontend_url: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

asyncpg_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
sync_url = asyncpg_url.replace("postgresql+asyncpg://", "postgresql://", 1)

database = Database(asyncpg_url)
metadata = MetaData()
engine = create_engine(sync_url)