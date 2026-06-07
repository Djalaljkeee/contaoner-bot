from maxapi.enums.attachment import AttachmentType
from maxapi.types.attachments import (
    AttachmentButton,
    ButtonsPayload,
    CallbackButton,
    RequestContactButton,
)


def confirm_kb() -> AttachmentButton:
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(
            buttons=[
                [CallbackButton(text="✅ Отправить", payload="maxlead:send")],
                [CallbackButton(text="✏ Изменить данные", payload="maxlead:edit")],
                [CallbackButton(text="✖ Отменить", payload="maxlead:cancel")],
            ]
        ),
    )


def phone_request_kb() -> AttachmentButton:
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(
            buttons=[
                [RequestContactButton(text="📱 Поделиться номером")],
                [CallbackButton(text="✖ Отменить", payload="maxlead:cancel")],
            ]
        ),
    )


def cancel_kb() -> AttachmentButton:
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(
            buttons=[
                [CallbackButton(text="✖ Отменить", payload="maxlead:cancel")],
            ]
        ),
    )
