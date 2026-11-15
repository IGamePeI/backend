from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from config import settings

engine: AsyncEngine = create_async_engine(
    settings.db_url,
    connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    poolclass=NullPool,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class Base(DeclarativeBase):
    pass
