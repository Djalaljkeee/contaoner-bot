from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main import main_menu_kb
from bot.services.users import upsert_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    await upsert_user(
        session,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "Здравствуйте! Это бот компании <b>ИЗ-КОНТЕЙНЕРОВ.РФ</b>.\n\n"
        "Мы делаем модульные решения из морских контейнеров: дома, офисы, кафе, "
        "магазины, склады. Выберите раздел в меню ниже.",
        reply_markup=main_menu_kb(),
    )
