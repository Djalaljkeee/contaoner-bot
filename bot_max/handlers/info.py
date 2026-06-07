import logging

from maxapi import Router
from maxapi.types.updates.message_created import MessageCreated

from bot_max.config import max_settings
from bot_max.keyboards.main import (
    ABOUT_BTN,
    ADV_BTN,
    CONTACTS_BTN,
    EQUIP_BTN,
    LAWYER_BTN,
    main_menu_kb,
)

log = logging.getLogger(__name__)
router = Router()

_ADVANTAGES = (
    "⭐ Преимущества Петрикс-Хоум\n\n"
    "1. Быстрое производство — готовый модуль за 30–60 дней\n"
    "2. Заводское качество — контроль на каждом этапе\n"
    "3. Прозрачные цены — всё включено в смету, без скрытых доплат\n"
    "4. Доставка по России — логистика под ключ\n"
    "5. Широкий выбор комплектаций — от эконом до премиум\n"
    "6. Гарантия 2 года — на конструкцию и отделку\n\n"
    "Более 200 реализованных проектов по всей стране!"
)

_EQUIPMENT = (
    "🧱 Комплектация стандартного модуля\n\n"
    "Конструкция:\n"
    "• Морской контейнер 20ft или 40ft\n"
    "• Усиленный металлокаркас\n"
    "• Утепление минеральной ватой 100–200 мм\n"
    "• Пароизоляция и ветрозащита\n\n"
    "Снаружи:\n"
    "• Фасад — профнастил, сайдинг или HPL-панели\n"
    "• Кровля с гидроизоляцией\n"
    "• Окна ПВХ двухкамерные\n"
    "• Входная металлическая дверь\n\n"
    "Внутри (стандарт):\n"
    "• Пол — OSB + ламинат\n"
    "• Стены — гипсокартон + окраска\n"
    "• Потолок — потолочная плитка или ПВХ-панели\n\n"
    "Дополнительно (по запросу):\n"
    "• Электрика под ключ (щит, розетки, освещение)\n"
    "• Санузел с душем\n"
    "• Терраса\n"
    "• Кондиционер\n"
)

_ABOUT = (
    f"👤 О компании Петрикс-Хоум\n\n"
    f"Основатель: {max_settings.company_founder}\n\n"
    "Петрикс-Хоум — производитель модульных домов и офисов "
    "из морских контейнеров. Работаем с 2018 года.\n\n"
    "Наша миссия — сделать качественное жильё и коммерческую "
    "недвижимость доступными для каждого.\n\n"
    "Специализация:\n"
    "• Жилые модульные дома\n"
    "• Офисы продаж и шоурумы\n"
    "• Глэмпинг-домики\n"
    "• Дачные домики\n"
    "• Санитарные блоки\n\n"
    f"Сайт: {max_settings.company_site}"
)

_LAWYER = (
    f"⚖️ Юридическая консультация\n\n"
    f"Юрист: {max_settings.company_lawyer}\n\n"
    "Мы оказываем бесплатную юридическую консультацию по вопросам:\n\n"
    "• Оформление договора купли-продажи\n"
    "• Регистрация объекта в Росреестре\n"
    "• Налоговые вопросы при покупке модульного дома\n"
    "• Разрешение на строительство и ввод в эксплуатацию\n"
    "• Земельные вопросы (перевод категории, аренда)\n\n"
    "Для получения консультации оставьте заявку — юрист свяжется в течение 1 рабочего дня.\n\n"
    f"📞 {max_settings.company_phone}"
)

_CONTACTS = (
    f"📞 Контакты Петрикс-Хоум\n\n"
    f"Телефон: {max_settings.company_phone}\n"
    f"Телефон: {max_settings.company_phone2}\n"
    f"Email: {max_settings.company_email}\n"
    f"Сайт: {max_settings.company_site}\n\n"
    f"Основатель: {max_settings.company_founder}\n\n"
    "Социальные сети:\n"
    f"• RUTUBE: {max_settings.social_rutube}\n"
    f"• ВКонтакте: vk.com/{max_settings.social_vk1}\n"
    f"• ВКонтакте: vk.com/{max_settings.social_vk2}\n"
    f"• Дзен: {max_settings.social_dzen}\n\n"
    "Режим работы: пн–пт 9:00–18:00 (МСК)"
)


@router.message_created.register
async def show_advantages(event: MessageCreated):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != ADV_BTN:
        return
    await event.message.answer(text=_ADVANTAGES, attachments=[main_menu_kb()])


@router.message_created.register
async def show_equipment(event: MessageCreated):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != EQUIP_BTN:
        return
    await event.message.answer(text=_EQUIPMENT, attachments=[main_menu_kb()])


@router.message_created.register
async def show_about(event: MessageCreated):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != ABOUT_BTN:
        return
    await event.message.answer(text=_ABOUT, attachments=[main_menu_kb()])


@router.message_created.register
async def show_lawyer(event: MessageCreated):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != LAWYER_BTN:
        return
    await event.message.answer(text=_LAWYER, attachments=[main_menu_kb()])


@router.message_created.register
async def show_contacts(event: MessageCreated):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != CONTACTS_BTN:
        return
    await event.message.answer(text=_CONTACTS, attachments=[main_menu_kb()])
