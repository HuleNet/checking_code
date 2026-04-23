from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from checking_service.infrastructure.core import get_settings_cached


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
