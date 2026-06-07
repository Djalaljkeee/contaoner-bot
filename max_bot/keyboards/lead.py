from maxapi.types import ButtonsPayload, CallbackButton, RequestContactButton


def request_contact_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [RequestContactButton(text="📱 Поделиться номером")],
            [CallbackButton(text="⬅️ Отмена", payload="menu:main")],
        ]
    )


def confirm_lead_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [
                CallbackButton(text="✅ Подтвердить", payload="lead:confirm"),
                CallbackButton(text="❌ Отмена", payload="menu:main"),
            ]
        ]
    )


def after_lead_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[[CallbackButton(text="⬅️ В главное меню", payload="menu:main")]]
    )
