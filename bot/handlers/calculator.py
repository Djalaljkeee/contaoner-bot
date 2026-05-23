import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import CalcOption, CalcOptionGroup, LeadSource, LeadType
from bot.keyboards.calculator import (
    delivery_kb,
    foundation_kb,
    insulation_kb,
    interior_kb,
    module_kb,
    result_kb,
    windows_kb,
)
from bot.keyboards.lead import use_name_kb
from bot.keyboards.main import CALC_BTN
from bot.services.calculator import (
    build_summary,
    calc_delivery,
    extract_calc_config,
    get_calc_options,
    list_delivery_cities,
)
from bot.services.users import upsert_user
from bot.states.calculator import CalcForm
from bot.states.lead import LeadForm

log = logging.getLogger(__name__)
router = Router()

_STEP_HEADERS = {
    "module":     "🧮 <b>Шаг 1/5 — Выберите модуль</b>",
    "insulation": "🧮 <b>Шаг 2/5 — Утепление</b>",
    "foundation": "🧮 <b>Шаг 3/5 — Фундамент</b>",
    "interior":   "🧮 <b>Шаг 4/5 — Внутренняя отделка</b>",
    "windows":    "🧮 <b>Шаг 5/5 — Остекление</b>",
    "delivery":   "🚚 <b>Доставка — выберите город или введите расстояние</b>\n"
                  "<i>Тариф: 55 ₽/км от Москвы (погрузка, крепление и сопровождение включены)</i>",
}


async def _send_or_edit(msg: Message, text: str, kb, calc_msg_id: int | None) -> int:
    if calc_msg_id:
        try:
            edited = await msg.bot.edit_message_text(
                text=text,
                chat_id=msg.chat.id,
                message_id=calc_msg_id,
                reply_markup=kb,
                parse_mode="HTML",
            )
            return edited.message_id
        except TelegramBadRequest:
            pass
    sent = await msg.answer(text, reply_markup=kb)
    return sent.message_id


@router.message(F.text == CALC_BTN)
async def start_calc(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    options = await get_calc_options(session, CalcOptionGroup.module)
    sent = await message.answer(_STEP_HEADERS["module"], reply_markup=module_kb(options))
    await state.set_state(CalcForm.choosing_module)
    await state.set_data({"calc_msg_id": sent.message_id})


@router.callback_query(F.data == "calc:restart")
async def restart_calc(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    options = await get_calc_options(session, CalcOptionGroup.module)
    try:
        await call.message.edit_text(_STEP_HEADERS["module"], reply_markup=module_kb(options))
        calc_msg_id = call.message.message_id
    except TelegramBadRequest:
        sent = await call.message.answer(_STEP_HEADERS["module"], reply_markup=module_kb(options))
        calc_msg_id = sent.message_id
    await state.set_state(CalcForm.choosing_module)
    await state.set_data({"calc_msg_id": calc_msg_id})
    await call.answer()


@router.callback_query(CalcForm.choosing_module, F.data.startswith("calc:mod:"))
async def on_module(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(call.data.split(":")[2])
    opt: CalcOption | None = await session.get(CalcOption, option_id)
    if not opt:
        await call.answer("Опция не найдена", show_alert=True)
        return

    data = await state.get_data()
    data.update(
        module_id=opt.id,
        module_title=opt.title,
        module_price=int(opt.price_delta),
        module_area_m2=float(opt.area_m2) if opt.area_m2 else None,
    )
    options = await get_calc_options(session, CalcOptionGroup.insulation)
    new_id = await _send_or_edit(
        call.message, _STEP_HEADERS["insulation"], insulation_kb(options), data.get("calc_msg_id")
    )
    data["calc_msg_id"] = new_id
    await state.set_state(CalcForm.choosing_insulation)
    await state.set_data(data)
    await call.answer()


@router.callback_query(CalcForm.choosing_insulation, F.data.startswith("calc:ins:"))
async def on_insulation(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(call.data.split(":")[2])
    opt: CalcOption | None = await session.get(CalcOption, option_id)
    if not opt:
        await call.answer("Опция не найдена", show_alert=True)
        return

    data = await state.get_data()
    data.update(ins_id=opt.id, ins_title=opt.title, ins_price_delta=int(opt.price_delta))
    options = await get_calc_options(session, CalcOptionGroup.foundation)
    new_id = await _send_or_edit(
        call.message, _STEP_HEADERS["foundation"], foundation_kb(options), data.get("calc_msg_id")
    )
    data["calc_msg_id"] = new_id
    await state.set_state(CalcForm.choosing_foundation)
    await state.set_data(data)
    await call.answer()


@router.callback_query(CalcForm.choosing_foundation, F.data.startswith("calc:fnd:"))
async def on_foundation(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(call.data.split(":")[2])
    opt: CalcOption | None = await session.get(CalcOption, option_id)
    if not opt:
        await call.answer("Опция не найдена", show_alert=True)
        return

    data = await state.get_data()
    data.update(fnd_id=opt.id, fnd_title=opt.title, fnd_price_delta=int(opt.price_delta))
    options = await get_calc_options(session, CalcOptionGroup.interior)
    new_id = await _send_or_edit(
        call.message, _STEP_HEADERS["interior"], interior_kb(options), data.get("calc_msg_id")
    )
    data["calc_msg_id"] = new_id
    await state.set_state(CalcForm.choosing_interior)
    await state.set_data(data)
    await call.answer()


@router.callback_query(CalcForm.choosing_interior, F.data.startswith("calc:int:"))
async def on_interior(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(call.data.split(":")[2])
    opt: CalcOption | None = await session.get(CalcOption, option_id)
    if not opt:
        await call.answer("Опция не найдена", show_alert=True)
        return

    data = await state.get_data()
    data.update(int_id=opt.id, int_title=opt.title, int_price_delta=int(opt.price_delta))
    options = await get_calc_options(session, CalcOptionGroup.windows)
    new_id = await _send_or_edit(
        call.message, _STEP_HEADERS["windows"], windows_kb(options), data.get("calc_msg_id")
    )
    data["calc_msg_id"] = new_id
    await state.set_state(CalcForm.choosing_windows)
    await state.set_data(data)
    await call.answer()


@router.callback_query(CalcForm.choosing_windows, F.data.startswith("calc:win:"))
async def on_windows(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(call.data.split(":")[2])
    opt: CalcOption | None = await session.get(CalcOption, option_id)
    if not opt:
        await call.answer("Опция не найдена", show_alert=True)
        return

    data = await state.get_data()
    data.update(win_id=opt.id, win_title=opt.title, win_price_delta=int(opt.price_delta))
    cities = await list_delivery_cities(session)
    new_id = await _send_or_edit(
        call.message, _STEP_HEADERS["delivery"], delivery_kb(cities), data.get("calc_msg_id")
    )
    data["calc_msg_id"] = new_id
    await state.set_state(CalcForm.choosing_delivery)
    await state.set_data(data)
    await call.answer()


@router.callback_query(CalcForm.choosing_delivery, F.data.startswith("calc:cit:"))
async def on_city(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    from bot.db.models import DeliveryCity

    city_id = int(call.data.split(":")[2])
    city: DeliveryCity | None = await session.get(DeliveryCity, city_id)
    if not city:
        await call.answer("Город не найден", show_alert=True)
        return

    data = await state.get_data()
    km = city.distance_km
    data.update(
        delivery_city=city.name,
        delivery_km=km,
        delivery_cost=calc_delivery(km),
    )
    await _show_result(call.message, state, data)
    await call.answer()


@router.callback_query(CalcForm.choosing_delivery, F.data == "calc:km")
async def on_manual_km(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        await call.message.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=data.get("calc_msg_id", call.message.message_id),
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass
    await call.message.answer("Введите расстояние от Москвы в км (только число, например: 500):")
    await state.set_state(CalcForm.entering_distance)
    await call.answer()


@router.message(CalcForm.entering_distance, F.text)
async def on_distance_entered(message: Message, state: FSMContext):
    raw = (message.text or "").strip().replace(" ", "").replace(",", "")
    try:
        km = int(raw)
        if km < 0 or km > 20000:
            raise ValueError
    except ValueError:
        await message.answer("Введите расстояние числом от 0 до 20 000 (км).")
        return

    data = await state.get_data()
    data.update(
        delivery_city=f"{km} км от Москвы",
        delivery_km=km,
        delivery_cost=calc_delivery(km),
    )
    await _show_result(message, state, data)


async def _show_result(target: Message, state: FSMContext, data: dict) -> None:
    summary = build_summary(data)
    sent = await target.answer(summary, reply_markup=result_kb())
    data["result_msg_id"] = sent.message_id
    await state.set_state(CalcForm.showing_result)
    await state.set_data(data)


@router.callback_query(CalcForm.showing_result, F.data == "calc:lead")
async def calc_to_lead(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    calc_config = extract_calc_config(data)

    await state.clear()

    user = await upsert_user(
        session,
        tg_id=call.from_user.id,
        username=call.from_user.username,
        full_name=call.from_user.full_name,
    )
    await state.set_state(LeadForm.waiting_name)
    await state.set_data(
        {
            "source": LeadSource.calculator.value,
            "lead_type": LeadType.calculator.value,
            "product_id": None,
            "product_title": None,
            "calc_config": calc_config,
            "name": None,
            "phone": None,
            "message_text": None,
        }
    )
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.answer()
    await call.message.answer(
        "Отличный выбор! Оставьте контакты — менеджер свяжется и уточнит детали.\n\n"
        "Как к вам обращаться?",
        reply_markup=use_name_kb(user.full_name),
    )
