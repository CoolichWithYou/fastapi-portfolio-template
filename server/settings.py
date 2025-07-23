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

    def get_connection(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )
