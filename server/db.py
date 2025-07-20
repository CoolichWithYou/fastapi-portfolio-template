from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

from server.settings import Settings

settings = Settings()

engine = create_async_engine(settings.get_connection(), echo=True)
