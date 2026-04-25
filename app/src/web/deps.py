from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import Settings
from src.core.db import async_session_maker


def get_settings() -> Settings:
    return Settings()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
