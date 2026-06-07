from maxapi.enums.attachment import AttachmentType
from maxapi.types.attachments import (
    AttachmentButton,
    ButtonsPayload,
    CallbackButton,
)

from bot_max.db.models import MaxCalcExtra, MaxCalcFinishingOption, MaxCalcInsulationOption, MaxCalcSizeOption
from bot_max.services.calculator import fmt


def size_kb(options: list[MaxCalcSizeOption]) -> AttachmentButton:
    rows = []
    for opt in options:
        label = f"{opt.title} — {fmt(opt.base_price)} ₽"
        rows.append([CallbackButton(text=label, payload=f"maxcalc:size:{opt.id}")])
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=rows),
    )


def insulation_kb(options: list[MaxCalcInsulationOption]) -> AttachmentButton:
    rows = []
    for opt in options:
        if opt.price_delta == 0:
            label = f"{opt.title} — включено"
        else:
            label = f"{opt.title} — +{fmt(opt.price_delta)} ₽"
        rows.append([CallbackButton(text=label, payload=f"maxcalc:ins:{opt.id}")])
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=rows),
    )


def finishing_kb(options: list[MaxCalcFinishingOption]) -> AttachmentButton:
    rows = []
    for opt in options:
        if opt.price_delta == 0:
            label = f"{opt.title} — включено"
        else:
            label = f"{opt.title} — +{fmt(opt.price_delta)} ₽"
        rows.append([CallbackButton(text=label, payload=f"maxcalc:fin:{opt.id}")])
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=rows),
    )


def extras_kb(
    options: list[MaxCalcExtra], selected: list[int]
) -> AttachmentButton:
    rows = []
    for opt in options:
        mark = "✅" if opt.id in selected else "⬜"
        label = f"{mark} {opt.title} +{fmt(opt.price_delta)} ₽"
        rows.append([CallbackButton(text=label, payload=f"maxcalc:ext_toggle:{opt.id}")])
    rows.append([CallbackButton(text="✅ Готово", payload="maxcalc:ext_done")])
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(buttons=rows),
    )


def result_kb() -> AttachmentButton:
    return AttachmentButton(
        type=AttachmentType.INLINE_KEYBOARD,
        payload=ButtonsPayload(
            buttons=[
                [CallbackButton(text="🔥 Получить смету", payload="maxcalc:lead")],
                [CallbackButton(text="🔄 Пересчитать", payload="maxcalc:restart")],
            ]
        ),
    )
