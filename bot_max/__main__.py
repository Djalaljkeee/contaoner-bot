import asyncio
import logging

from maxapi import Bot, Dispatcher, Router
from maxapi.context.context import MemoryContext
from maxapi.filters.middleware import BaseMiddleware
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot_max.config import max_settings
from bot_max.db.base import SessionLocal, engine
from bot_max.db.models import MaxBase
from bot_max.handlers import catalog, calculator, info, lead, start

log = logging.getLogger(__name__)


def _migrate_schema_max(sync_conn) -> None:
    inspector = sa_inspect(sync_conn)
    # Drop if max_leads exists but is missing required columns
    if inspector.has_table("max_leads"):
        cols = {c["name"] for c in inspector.get_columns("max_leads")}
        if "product_title" not in cols:
            log.warning("Old max_ schema detected — dropping and recreating")
            MaxBase.metadata.drop_all(sync_conn)
    MaxBase.metadata.create_all(sync_conn)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(self, handler, event_object, data):
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event_object, data)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    async with engine.begin() as conn:
        await conn.run_sync(_migrate_schema_max)

    bot = Bot(token=max_settings.max_bot_token)
    dp = Dispatcher(storage=MemoryContext)

    session_mw = DbSessionMiddleware(SessionLocal)
    dp.register_outer_middleware(session_mw)

    dp.include_routers(
        start.router,
        calculator.router,
        catalog.router,
        lead.router,
        info.router,
    )

    log.info("Starting MAX bot (long polling)...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
