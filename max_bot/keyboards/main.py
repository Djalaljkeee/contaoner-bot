from maxapi.types import ButtonsPayload, CallbackButton


def main_menu_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [
                CallbackButton(text="🏠 Проекты и цены", payload="menu:catalog"),
                CallbackButton(text="💰 Калькулятор", payload="menu:calc"),
            ],
            [
                CallbackButton(text="⭐ Преимущества", payload="menu:advantages"),
                CallbackButton(text="🧱 Комплектация", payload="menu:specs"),
            ],
            [
                CallbackButton(text="👤 О компании", payload="menu:about"),
                CallbackButton(text="⚖️ Юрист", payload="menu:legal"),
            ],
            [
                CallbackButton(text="📞 Контакты", payload="menu:contacts"),
                CallbackButton(text="📝 Оставить заявку", payload="lead:start"),
            ],
        ]
    )


def back_to_menu_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[[CallbackButton(text="⬅️ В главное меню", payload="menu:main")]]
    )
