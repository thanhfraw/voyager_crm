from pydantic_settings import BaseSettings
from databases import Database
from sqlalchemy import create_engine, MetaData

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    frontend_url: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()

database = Database(settings.database_url)
metadata = MetaData()
engine = create_engine(settings.database_url)
