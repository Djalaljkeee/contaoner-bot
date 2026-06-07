from maxapi.types import ButtonsPayload, CallbackButton

from max_bot.services.calculator import (
    FINISH_LABELS,
    INSULATION_LABELS,
    OPTION_LABELS,
    SIZE_LABELS,
)


def size_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [CallbackButton(text=label, payload=f"calc:size:{i}")]
            for i, label in enumerate(SIZE_LABELS)
        ]
        + [[CallbackButton(text="⬅️ В главное меню", payload="menu:main")]]
    )


def insulation_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [CallbackButton(text=label, payload=f"calc:ins:{i}")]
            for i, label in enumerate(INSULATION_LABELS)
        ]
        + [[CallbackButton(text="⬅️ В главное меню", payload="menu:main")]]
    )


def finish_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [CallbackButton(text=label, payload=f"calc:fin:{i}")]
            for i, label in enumerate(FINISH_LABELS)
        ]
        + [[CallbackButton(text="⬅️ В главное меню", payload="menu:main")]]
    )


def options_kb(selected: list[str]) -> ButtonsPayload:
    rows = []
    for i, label in enumerate(OPTION_LABELS):
        check = "✅ " if label in selected else ""
        rows.append([CallbackButton(text=f"{check}{label}", payload=f"calc:opt:{i}")])
    rows.append([CallbackButton(text="✔️ Готово → показать итог", payload="calc:done")])
    rows.append([CallbackButton(text="⬅️ В главное меню", payload="menu:main")])
    return ButtonsPayload(buttons=rows)


def result_kb() -> ButtonsPayload:
    return ButtonsPayload(
        buttons=[
            [CallbackButton(text="🔥 Получить смету / оставить заявку", payload="lead:calc")],
            [CallbackButton(text="🔄 Рассчитать заново", payload="menu:calc")],
            [CallbackButton(text="⬅️ В главное меню", payload="menu:main")],
        ]
    )
