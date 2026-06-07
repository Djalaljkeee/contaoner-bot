from maxapi.enums.attachment import AttachmentType
from maxapi.types.attachments import (
    AttachmentButton,
    ButtonsPayload,
    MessageButton,
)

CATALOG_BTN = "🏠 Проекты и цены"
CALC_BTN = "💰 Калькулятор стоимости"
ADV_BTN = "⭐ Преимущества"
EQUIP_BTN = "🧱 Комплектация модуля"
ABOUT_BTN = "👤 О компании"
LAWYER_BTN = "⚖️ Юридическая консультация"
CONTACTS_BTN = "📞 Контакты"
LEAD_BTN = "📝 Оставить заявку"


def main_menu_kb() -> AttachmentButton:
    buttons = [
        [MessageButton(text=CATALOG_BTN), MessageButton(text=CALC_BTN)],
        [MessageButton(text=ADV_BTN), MessageButton(text=EQUIP_BTN)],
        [MessageButton(text=ABOUT_BTN), MessageButton(text=LAWYER_BTN)],
        [MessageButton(text=CONTACTS_BTN), MessageButton(text=LEAD_BTN)],
    ]
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=buttons),
    )
