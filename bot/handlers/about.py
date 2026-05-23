from aiogram import F, Router
from aiogram.types import Message

from bot.config import settings
from bot.keyboards.main import ABOUT_BTN, CONTACTS_BTN, main_menu_kb

router = Router()


@router.message(F.text == ABOUT_BTN)
async def about(message: Message):
    text = (
        f"<b>{settings.company_name}</b>\n\n"
        "Строим дома и офисы из морских контейнеров 20ft и 40ft.\n\n"
        "<b>Наши проекты:</b>\n"
        "• Жилые дома — от компактных 14 м² до двухэтажных 56 м²\n"
        "• Модульные офисы и офисные комплексы\n\n"
        "<b>Почему выбирают нас:</b>\n"
        "• Прозрачный прайс — все цены опубликованы\n"
        "• Калькулятор прямо в боте — считайте не выходя\n"
        "• Быстрая сборка — от 25 до 90 дней\n"
        "• Доставка по России — 55 ₽/км от Москвы\n"
        "• Погрузка, крепление и сопровождение включены\n\n"
        "Работаем на InSales — полноценный интернет-магазин с корзиной и предзаказом."
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.message(F.text == CONTACTS_BTN)
async def contacts(message: Message):
    text = (
        f"<b>Контакты {settings.company_name}</b>\n\n"
        f"📞 {settings.company_phone}\n"
        f"📞 {settings.company_phone2}\n"
        f"📧 {settings.company_email}\n"
        f"🌐 {settings.company_site}\n\n"
        f"📍 {settings.company_address_base}\n"
        f"🏢 {settings.company_address_office}\n\n"
        "Удобнее всего — воспользуйтесь калькулятором или оставьте заявку,\n"
        "менеджер сам свяжется в рабочее время."
    )
    await message.answer(text, reply_markup=main_menu_kb())
