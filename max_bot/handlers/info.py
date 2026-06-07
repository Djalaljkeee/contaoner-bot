from maxapi import Dispatcher, Router
from maxapi.filters import F
from maxapi.types import MessageCallback

from max_bot.config import settings
from max_bot.keyboards.main import back_to_menu_kb

router = Router()

_ADVANTAGES_TEXT = (
    "⭐ Преимущества «Петрикс-Хоум»\n\n"
    "🏭 Собственное производство — полный контроль качества\n\n"
    "❄️ Зимнее исполнение — утепление 100–150 мм (до 200 мм)\n\n"
    "⚡ Скорость — готовый модуль от 7 дней\n\n"
    "🛡️ Гарантия — 12 месяцев на все виды работ\n\n"
    "🚚 Доставка по всей России\n\n"
    "💼 Любая форма оплаты — наличные, безнал, рассрочка"
)

_SPECS_TEXT = (
    "🧱 Базовая комплектация модуля\n\n"
    "🔩 Каркас: усиленный морской контейнер (20 или 40 футов)\n"
    "🧊 Утепление: пол/стены/потолок 100 мм (усиление до 200 мм)\n"
    "🏗 Внешняя отделка: профлист / сайдинг / имитация бруса / фальц\n"
    "🪵 Внутренняя отделка: вагонка / ОСБ / влагостойкий гипсокартон\n"
    "🪜 Пол: фанера 18 мм + линолеум / ламинат 33 класса\n"
    "🔲 Окна: ПВХ двухкамерные энергосберегающие\n"
    "🚪 Дверь: металлическая утеплённая\n"
    "⚡ Электрика: полная разводка под ключ, щиток с УЗО\n\n"
    "📐 Ориентировочные цены:\n"
    "  • 20 футов (6×2.4 м) — от 168 000 ₽\n"
    "  • 40 футов (12×2.4 м) — от 285 000 ₽"
)

_ABOUT_TEXT = (
    "👤 О компании «Петрикс-Хоум»\n\n"
    "Основатель и CEO — Петриков Роман Андреевич.\n\n"
    "📊 Ключевые цифры:\n"
    "  • 100+ реализованных проектов\n"
    "  • Оборот 25 млн ₽ за 1-й квартал 2024\n"
    "  • Утепление 100–150 мм (опция 200 мм)\n"
    "  • Гарантия 12 месяцев\n"
    "  • Срок изготовления от 7 дней\n\n"
    "📺 Наши соцсети и блоги:\n"
    "  • RUTUBE: Кавказский Бульвар\n"
    "  • ВКонтакте: vk.com/petrixlogistic\n"
    "  • Дзен, Яндекс.Музыка\n"
    "  • Официальный канал в MAX"
)

_LEGAL_TEXT = (
    "⚖️ Юридическая консультация\n\n"
    "Руководитель юридической службы — Юлия.\n\n"
    "Услуги (бесплатно для клиентов компании):\n"
    "✅ Проверка договоров купли-продажи\n"
    "✅ Юридическое сопровождение сделок\n"
    "✅ Защита прав покупателей\n"
    "✅ Работа с юридическими лицами\n"
    "✅ Консультации по земельным вопросам\n\n"
    "📩 Для связи с юристом используйте бота: @Lawyer_helpp_bot"
)

_CONTACTS_TEXT = (
    f"📞 Контакты «{settings.company_name}»\n\n"
    f"📱 Телефон 1: {settings.company_phone}\n"
    f"📱 Телефон 2: {settings.company_phone2}\n"
    f"📧 E-mail: {settings.company_email}\n"
    f"🌐 Сайт: {settings.company_site}\n\n"
    "📄 Документы:\n"
    f"  • Оферта: {settings.company_site}/page/agreement\n"
    f"  • Политика конфиденциальности: {settings.company_site}/page/privacy\n\n"
    "Мы работаем с 9:00 до 21:00 (МСК), без выходных."
)


@router.message_callback(F.callback.payload == "menu:advantages")
async def show_advantages(event: MessageCallback) -> None:
    await event.edit(_ADVANTAGES_TEXT, attachments=[back_to_menu_kb().pack()])


@router.message_callback(F.callback.payload == "menu:specs")
async def show_specs(event: MessageCallback) -> None:
    await event.edit(_SPECS_TEXT, attachments=[back_to_menu_kb().pack()])


@router.message_callback(F.callback.payload == "menu:about")
async def show_about(event: MessageCallback) -> None:
    await event.edit(_ABOUT_TEXT, attachments=[back_to_menu_kb().pack()])


@router.message_callback(F.callback.payload == "menu:legal")
async def show_legal(event: MessageCallback) -> None:
    await event.edit(_LEGAL_TEXT, attachments=[back_to_menu_kb().pack()])


@router.message_callback(F.callback.payload == "menu:contacts")
async def show_contacts(event: MessageCallback) -> None:
    await event.edit(_CONTACTS_TEXT, attachments=[back_to_menu_kb().pack()])


def register(dp: Dispatcher) -> None:
    dp.include_routers(router)
