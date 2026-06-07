import logging

from maxapi import Router
from maxapi.context.base import BaseContext
from maxapi.types.updates.message_callback import MessageCallback
from maxapi.types.updates.message_created import MessageCreated
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.keyboards.calculator import (
    extras_kb,
    finishing_kb,
    insulation_kb,
    result_kb,
    size_kb,
)
from bot_max.keyboards.main import CALC_BTN
from bot_max.services.calculator import (
    build_summary,
    extract_config,
    get_extras,
    get_finishing_options,
    get_insulation_options,
    get_size_options,
)
from bot_max.states.calculator import MaxCalcForm

log = logging.getLogger(__name__)
router = Router()


@router.message_created.register
async def start_calc(event: MessageCreated, context: BaseContext, session: AsyncSession):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != CALC_BTN:
        return
    await context.clear()
    options = await get_size_options(session)
    await context.set_state(MaxCalcForm.choosing_size)
    await event.message.answer(
        text="🧮 Шаг 1/4 — Выберите размер модуля:",
        attachments=[size_kb(options)],
    )


@router.message_callback.register
async def calc_restart(event: MessageCallback, context: BaseContext, session: AsyncSession):
    if event.callback.payload != "maxcalc:restart":
        return
    await context.clear()
    options = await get_size_options(session)
    await context.set_state(MaxCalcForm.choosing_size)
    await event.edit(
        text="🧮 Шаг 1/4 — Выберите размер модуля:",
        attachments=[size_kb(options)],
    )
    await event.ack()


@router.message_callback.register
async def on_size(
    event: MessageCallback, context: BaseContext, session: AsyncSession
):
    payload = event.callback.payload or ""
    if not payload.startswith("maxcalc:size:"):
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.choosing_size):
        await event.ack()
        return
    try:
        opt_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    opt = await session.get(__import__("bot_max.db.models", fromlist=["MaxCalcSizeOption"]).MaxCalcSizeOption, opt_id)
    if not opt:
        await event.ack(notification="Опция не найдена")
        return

    await context.update_data(
        size_id=opt.id,
        size_title=opt.title,
        size_base_price=opt.base_price,
    )
    options = await get_insulation_options(session)
    await context.set_state(MaxCalcForm.choosing_insulation)
    await event.edit(
        text="🧮 Шаг 2/4 — Выберите утепление:",
        attachments=[insulation_kb(options)],
    )
    await event.ack()


@router.message_callback.register
async def on_insulation(
    event: MessageCallback, context: BaseContext, session: AsyncSession
):
    payload = event.callback.payload or ""
    if not payload.startswith("maxcalc:ins:"):
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.choosing_insulation):
        await event.ack()
        return
    try:
        opt_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    from bot_max.db.models import MaxCalcInsulationOption
    opt = await session.get(MaxCalcInsulationOption, opt_id)
    if not opt:
        await event.ack(notification="Опция не найдена")
        return

    await context.update_data(
        insulation_id=opt.id,
        insulation_title=opt.title,
        insulation_delta=opt.price_delta,
    )
    options = await get_finishing_options(session)
    await context.set_state(MaxCalcForm.choosing_finishing)
    await event.edit(
        text="🧮 Шаг 3/4 — Выберите отделку:",
        attachments=[finishing_kb(options)],
    )
    await event.ack()


@router.message_callback.register
async def on_finishing(
    event: MessageCallback, context: BaseContext, session: AsyncSession
):
    payload = event.callback.payload or ""
    if not payload.startswith("maxcalc:fin:"):
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.choosing_finishing):
        await event.ack()
        return
    try:
        opt_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    from bot_max.db.models import MaxCalcFinishingOption
    opt = await session.get(MaxCalcFinishingOption, opt_id)
    if not opt:
        await event.ack(notification="Опция не найдена")
        return

    await context.update_data(
        finishing_id=opt.id,
        finishing_title=opt.title,
        finishing_delta=opt.price_delta,
        selected_extras_ids=[],
        selected_extras_titles=[],
        extras_delta=0,
    )
    extras = await get_extras(session)
    await context.set_state(MaxCalcForm.choosing_extras)
    await event.edit(
        text="🧮 Шаг 4/4 — Выберите дополнительные опции (можно несколько):",
        attachments=[extras_kb(extras, [])],
    )
    await event.ack()


@router.message_callback.register
async def on_extra_toggle(
    event: MessageCallback, context: BaseContext, session: AsyncSession
):
    payload = event.callback.payload or ""
    if not payload.startswith("maxcalc:ext_toggle:"):
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.choosing_extras):
        await event.ack()
        return
    try:
        extra_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    from bot_max.db.models import MaxCalcExtra
    extra = await session.get(MaxCalcExtra, extra_id)
    if not extra:
        await event.ack(notification="Опция не найдена")
        return

    data = await context.get_data()
    selected_ids: list[int] = list(data.get("selected_extras_ids", []))
    selected_titles: list[str] = list(data.get("selected_extras_titles", []))
    extras_delta: int = int(data.get("extras_delta", 0))

    if extra_id in selected_ids:
        selected_ids.remove(extra_id)
        if extra.title in selected_titles:
            selected_titles.remove(extra.title)
        extras_delta -= extra.price_delta
    else:
        selected_ids.append(extra_id)
        selected_titles.append(extra.title)
        extras_delta += extra.price_delta

    await context.update_data(
        selected_extras_ids=selected_ids,
        selected_extras_titles=selected_titles,
        extras_delta=max(0, extras_delta),
    )

    extras = await get_extras(session)
    await event.edit(
        text="🧮 Шаг 4/4 — Выберите дополнительные опции (можно несколько):",
        attachments=[extras_kb(extras, selected_ids)],
    )
    await event.ack()


@router.message_callback.register
async def on_extras_done(
    event: MessageCallback, context: BaseContext
):
    if event.callback.payload != "maxcalc:ext_done":
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.choosing_extras):
        await event.ack()
        return

    data = await context.get_data()
    summary = build_summary(data)
    await context.set_state(MaxCalcForm.showing_result)
    await event.edit(
        text=summary,
        attachments=[result_kb()],
    )
    await event.ack()


@router.message_callback.register
async def calc_to_lead(event: MessageCallback, context: BaseContext):
    if event.callback.payload != "maxcalc:lead":
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxCalcForm.showing_result):
        await event.ack()
        return

    data = await context.get_data()
    calc_config = extract_config(data)
    await context.clear()
    await context.update_data(
        calc_config=calc_config,
        product_title=None,
        from_calc=True,
    )
    from bot_max.keyboards.lead import cancel_kb
    from bot_max.states.lead import MaxLeadForm
    await context.set_state(MaxLeadForm.waiting_name)
    await event.edit(
        text=(
            "Отличный выбор! Оставьте контакты — менеджер свяжется и уточнит детали.\n\n"
            "Как к вам обращаться?"
        ),
        attachments=[cancel_kb()],
    )
    await event.ack()
