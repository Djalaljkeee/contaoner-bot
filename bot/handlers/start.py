from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main import main_menu_kb
from bot.services.users import upsert_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await upsert_user(
        session,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "Добро пожаловать! Это бот компании <b>КОНТЕЙНЕР 24</b>.\n\n"
        "Мы строим дома и офисы из морских контейнеров 20ft и 40ft — "
        "готовые объекты с прозрачным прайсом и доставкой по России.\n\n"
        "Воспользуйтесь калькулятором, чтобы рассчитать стоимость вашего проекта,\n"
        "или выберите готовую модель в каталоге.",
        reply_markup=main_menu_kb(),
    )
