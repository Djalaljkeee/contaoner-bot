from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot_max.config import max_settings

engine = create_async_engine(max_settings.max_db_url, echo=False, future=True)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
