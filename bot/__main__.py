import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import settings
from bot.db.base import SessionLocal, engine
from bot.db.models import Base
from bot.handlers import about, calculator, catalog, lead, start


class DbSessionMiddleware:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(self, handler, event, data):
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    session_mw = DbSessionMiddleware(SessionLocal)
    dp.message.middleware(session_mw)
    dp.callback_query.middleware(session_mw)

    dp.include_router(start.router)
    dp.include_router(calculator.router)
    dp.include_router(catalog.router)
    dp.include_router(lead.router)
    dp.include_router(about.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
