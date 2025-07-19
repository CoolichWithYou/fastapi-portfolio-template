from sqlalchemy import create_engine

from server.settings import Settings

settings = Settings()

engine = create_engine(settings.get_connection())
