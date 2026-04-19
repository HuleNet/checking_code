from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from checking_service.infrastructure.config import get_settings_cached


settings = get_settings_cached()
engine = create_async_engine(
    url=settings.db_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db
