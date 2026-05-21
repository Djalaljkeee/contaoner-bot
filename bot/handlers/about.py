from aiogram import F, Router
from aiogram.types import Message

from bot.config import settings
from bot.keyboards.main import ABOUT_BTN, CONTACTS_BTN, main_menu_kb

router = Router()


@router.message(F.text == ABOUT_BTN)
async def about(message: Message):
    text = (
        "<b>ИЗ-КОНТЕЙНЕРОВ.РФ</b>\n\n"
        "Мы делаем модульные решения из морских контейнеров под ключ: жилые дома, "
        "гостевые домики, офисы и шоурумы, кафе, магазины, склады, бани, бассейны, "
        "бункеры и спецобъекты.\n\n"
        "<b>Почему контейнер?</b>\n"
        "• Долговечность — сталь 1,5–2 мм со спецпокрытием\n"
        "• Мобильность — перевозятся фурой или манипулятором\n"
        "• Прозрачная цена — контейнер + отделка + работа\n"
        "• Гибкость — собираем любые формы, как из лего\n\n"
        "Выполняем проекты на нашем производстве и отгружаем готовыми."
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == CONTACTS_BTN)
async def contacts(message: Message):
    text = (
        "<b>Контакты</b>\n\n"
        f"Телефон: {settings.company_phone}\n"
        f"Почта: {settings.company_email}\n"
        f"Сайт: {settings.company_site}\n\n"
        "Удобнее всего — оставьте заявку через бота, менеджер сам свяжется."
    )
    await message.answer(text, reply_markup=main_menu_kb())
