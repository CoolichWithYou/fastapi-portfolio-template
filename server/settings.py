from pydantic_settings import BaseSettings

from server.utility import singleton


@singleton
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    REDIS_URL: str
    STATIC_DIRECTORY: str

    def get_connection(self):
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.DB_HOST
        port = self.DB_PORT
        db = self.POSTGRES_DB
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
