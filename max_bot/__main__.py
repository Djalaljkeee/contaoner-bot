import asyncio
import logging

from maxapi import Bot, Dispatcher

from max_bot.config import settings
from max_bot.db.base import init_db
from max_bot.handlers import calculator, catalog, info, lead, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()
    logger.info("База данных инициализирована")

    bot = Bot(token=settings.max_bot_token)
    dp = Dispatcher()

    start.register(dp)
    catalog.register(dp)
    info.register(dp)
    calculator.register(dp)
    lead.register(dp)

    logger.info("Запуск бота в режиме Long Polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
