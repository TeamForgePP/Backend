from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import Session


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    async with Session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
