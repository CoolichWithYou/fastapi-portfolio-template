from sqlalchemy.ext.asyncio import create_async_engine

from server.settings import Settings

settings = Settings()

engine = create_async_engine(settings.get_connection(), echo=True)
