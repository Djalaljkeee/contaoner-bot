import json

from maxapi import Dispatcher, Router
from maxapi.context import BaseContext
from maxapi.filters import F
from maxapi.types import MessageCallback

from max_bot.keyboards.calculator import (
    finish_kb,
    insulation_kb,
    options_kb,
    result_kb,
    size_kb,
)
from max_bot.services.calculator import (
    FINISH_LABELS,
    INSULATION_LABELS,
    OPTION_LABELS,
    SIZE_LABELS,
    CalcConfig,
)
from max_bot.states.calculator import CalcForm

router = Router()


@router.message_callback(F.callback.payload == "menu:calc")
async def start_calc(event: MessageCallback, context: BaseContext) -> None:
    await context.clear()
    await context.set_state(CalcForm.choosing_size)
    await event.edit(
        "💰 Калькулятор стоимости\n\nШаг 1/4 — Выберите размер модуля:",
        attachments=[size_kb().pack()],
    )


@router.message_callback(
    F.callback.payload.startswith("calc:size:"),
    states=[CalcForm.choosing_size],
)
async def choose_size(event: MessageCallback, context: BaseContext) -> None:
    payload = event.callback.payload or ""
    try:
        idx = int(payload.split(":")[-1])
    except (ValueError, IndexError):
        idx = 0
    size = SIZE_LABELS[max(0, min(idx, len(SIZE_LABELS) - 1))]

    await context.update_data(size=size)
    await context.set_state(CalcForm.choosing_insulation)

    from max_bot.services.calculator import BASE_PRICES
    base = BASE_PRICES[size]
    await event.edit(
        f"✅ Размер: {size} (базовая цена {base:,} ₽)\n\n"
        "Шаг 2/4 — Выберите утепление:".replace(",", " "),
        attachments=[insulation_kb().pack()],
    )


@router.message_callback(
    F.callback.payload.startswith("calc:ins:"),
    states=[CalcForm.choosing_insulation],
)
async def choose_insulation(event: MessageCallback, context: BaseContext) -> None:
    payload = event.callback.payload or ""
    try:
        idx = int(payload.split(":")[-1])
    except (ValueError, IndexError):
        idx = 0
    insulation = INSULATION_LABELS[max(0, min(idx, len(INSULATION_LABELS) - 1))]

    data = await context.get_data()
    await context.update_data(insulation=insulation)
    await context.set_state(CalcForm.choosing_finish)

    cfg = CalcConfig(size=data.get("size", ""), insulation=insulation)
    await event.edit(
        f"✅ Утепление: {insulation}\n\n"
        "Шаг 3/4 — Выберите тип отделки:",
        attachments=[finish_kb().pack()],
    )


@router.message_callback(
    F.callback.payload.startswith("calc:fin:"),
    states=[CalcForm.choosing_finish],
)
async def choose_finish(event: MessageCallback, context: BaseContext) -> None:
    payload = event.callback.payload or ""
    try:
        idx = int(payload.split(":")[-1])
    except (ValueError, IndexError):
        idx = 0
    finish = FINISH_LABELS[max(0, min(idx, len(FINISH_LABELS) - 1))]

    await context.update_data(finish=finish)
    await context.set_state(CalcForm.choosing_options)

    data = await context.get_data()
    await event.edit(
        f"✅ Отделка: {finish}\n\n"
        "Шаг 4/4 — Добавьте опции (можно несколько, нажмите ✔️ Готово когда выберете):",
        attachments=[options_kb([]).pack()],
    )


@router.message_callback(
    F.callback.payload.startswith("calc:opt:"),
    states=[CalcForm.choosing_options],
)
async def toggle_option(event: MessageCallback, context: BaseContext) -> None:
    payload = event.callback.payload or ""
    try:
        idx = int(payload.split(":")[-1])
    except (ValueError, IndexError):
        await event.ack()
        return

    label = OPTION_LABELS[max(0, min(idx, len(OPTION_LABELS) - 1))]
    data = await context.get_data()
    selected: list[str] = data.get("options", [])

    if label in selected:
        selected = [o for o in selected if o != label]
    else:
        selected = selected + [label]

    await context.update_data(options=selected)

    await event.edit(
        "Шаг 4/4 — Добавьте опции (можно несколько, нажмите ✔️ Готово когда выберете):\n\n"
        + (f"Выбрано: {', '.join(selected)}" if selected else "Нет выбранных опций"),
        attachments=[options_kb(selected).pack()],
    )


@router.message_callback(
    F.callback.payload == "calc:done",
    states=[CalcForm.choosing_options],
)
async def show_result(event: MessageCallback, context: BaseContext) -> None:
    data = await context.get_data()
    cfg = CalcConfig(
        size=data.get("size", ""),
        insulation=data.get("insulation", ""),
        finish=data.get("finish", ""),
        options=data.get("options", []),
    )
    await context.update_data(calc_config=json.dumps(cfg.to_dict(), ensure_ascii=False))
    await context.set_state(CalcForm.showing_result)

    text = (
        "🎉 Ориентировочная стоимость вашего модуля:\n\n"
        + cfg.summary()
        + "\n\n⚠️ Точная смета формируется после бесплатной консультации с менеджером."
    )
    await event.edit(text, attachments=[result_kb().pack()])


def register(dp: Dispatcher) -> None:
    dp.include_routers(router)
