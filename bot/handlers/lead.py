import logging
from typing import Optional

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.models import Admin, AdminRole, LeadSource, User
from bot.keyboards.lead import (
    CANCEL_BTN,
    SKIP_BTN,
    confirm_kb,
    message_kb,
    phone_kb,
    use_name_kb,
)
from bot.keyboards.main import LEAD_BTN, main_menu_kb
from bot.services.catalog import get_product_with_photos
from bot.services.leads import create_lead, take_lead
from bot.services.notifications import notify_managers
from bot.services.users import set_user_name, set_user_phone, upsert_user
from bot.states.lead import LeadForm
from bot.utils.phone import normalize_phone

log = logging.getLogger(__name__)
router = Router()


# ---------- entry ----------
async def _start(
    target: Message,
    *,
    source: LeadSource,
    product_id: Optional[int],
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
    username: Optional[str],
    default_name: Optional[str],
) -> None:
    user = await upsert_user(session, user_id, username, default_name)
    data: dict = {
        "source": source.value,
        "product_id": product_id,
        "product_title": None,
        "name": None,
        "phone": None,
        "message_text": None,
    }
    if product_id:
        product = await get_product_with_photos(session, product_id)
        if product:
            title = product.title
            if product.area_m2:
                title += f", {int(product.area_m2)} м²"
            data["product_title"] = title
    await state.set_state(LeadForm.waiting_name)
    await state.set_data(data)
    intro = (
        f"Заявка по проекту: <b>{data['product_title']}</b>.\n"
        "Менеджер свяжется в рабочее время."
        if data["product_title"]
        else "Оставьте заявку — менеджер свяжется в рабочее время."
    )
    await target.answer(
        f"{intro}\n\nКак к вам обращаться?",
        reply_markup=use_name_kb(user.full_name),
    )


@router.message(F.text == LEAD_BTN)
async def lead_from_menu(message: Message, state: FSMContext, session: AsyncSession):
    await _start(
        message,
        source=LeadSource.main_menu,
        product_id=None,
        state=state,
        session=session,
        user_id=message.from_user.id,
        username=message.from_user.username,
        default_name=message.from_user.full_name,
    )


@router.callback_query(F.data.startswith("lead_start:"))
async def lead_from_product(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()
    product_id = int(call.data.split(":", 1)[1])
    await _start(
        call.message,
        source=LeadSource.product_card,
        product_id=product_id,
        state=state,
        session=session,
        user_id=call.from_user.id,
        username=call.from_user.username,
        default_name=call.from_user.full_name,
    )


# ---------- cancel ----------
@router.message(F.text == CANCEL_BTN)
async def cancel_msg(message: Message, state: FSMContext):
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu_kb())


@router.callback_query(F.data == "lead_cancel")
async def cancel_cb(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer("Отменено")
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.message.answer("Отменено.", reply_markup=main_menu_kb())


# ---------- step 1: name ----------
@router.message(LeadForm.waiting_name, F.text)
async def step_name(message: Message, state: FSMContext, session: AsyncSession):
    text = (message.text or "").strip()
    if text.startswith("Использовать «") and text.endswith("»"):
        text = text[len("Использовать «") : -1]
    if len(text) < 2 or len(text) > 80 or text.replace(" ", "").isdigit():
        await message.answer("Имя выглядит странно — попробуйте ещё раз.")
        return
    await set_user_name(session, message.from_user.id, text)
    await state.update_data(name=text)
    user = await session.get(User, message.from_user.id)
    await state.set_state(LeadForm.waiting_phone)
    await message.answer(
        "Оставьте номер — менеджер перезвонит.\n"
        "Можно поделиться контактом одним тапом или ввести вручную.",
        reply_markup=phone_kb(user.phone if user else None),
    )


# ---------- step 2: phone ----------
@router.message(LeadForm.waiting_phone, F.contact)
async def step_phone_contact(message: Message, state: FSMContext, session: AsyncSession):
    contact = message.contact
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(
            "Пожалуйста, поделитесь собственным контактом или введите номер вручную."
        )
        return
    phone = normalize_phone(contact.phone_number)
    if not phone:
        await message.answer("Не удалось распознать номер. Введите вручную.")
        return
    await _on_phone_ok(message, state, session, phone)


@router.message(LeadForm.waiting_phone, F.text)
async def step_phone_text(message: Message, state: FSMContext, session: AsyncSession):
    text = (message.text or "").strip()
    if text.startswith("Использовать "):
        text = text[len("Использовать ") :]
    phone = normalize_phone(text)
    if not phone:
        await message.answer(
            "Не распознал номер. Пример: +7 (985) 888-58-86.\nПопробуйте ещё раз."
        )
        return
    await _on_phone_ok(message, state, session, phone)


async def _on_phone_ok(
    message: Message, state: FSMContext, session: AsyncSession, phone: str
) -> None:
    await set_user_phone(session, message.from_user.id, phone)
    await state.update_data(phone=phone)
    await state.set_state(LeadForm.waiting_message)
    await message.answer(
        "Опишите задачу: размеры, сроки, бюджет, регион. Можно пропустить.",
        reply_markup=message_kb(),
    )


# ---------- step 3: message ----------
@router.message(LeadForm.waiting_message, F.text)
async def step_message(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    body: Optional[str]
    if text == SKIP_BTN or not text:
        body = None
    else:
        body = text[:2000]
    await state.update_data(message_text=body)
    await _ask_confirmation(message, state)


async def _ask_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    parts = [
        "<b>Проверьте заявку</b>",
        "",
        f"Имя: {data['name']}",
        f"Телефон: <code>{data['phone']}</code>",
    ]
    if data.get("product_title"):
        parts.append(f"Проект: {data['product_title']}")
    parts.append(f"Сообщение: {data.get('message_text') or '—'}")
    parts.append("")
    parts.append("Отправляем?")
    await state.set_state(LeadForm.confirming)
    await message.answer("\n".join(parts), reply_markup=confirm_kb())


# ---------- step 4: confirm ----------
@router.callback_query(LeadForm.confirming, F.data == "lead_send")
async def step_send(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
):
    data = await state.get_data()
    lead = await create_lead(
        session,
        user_id=call.from_user.id,
        name=data["name"],
        phone=data["phone"],
        message=data.get("message_text"),
        source=LeadSource(data["source"]),
        product_id=data.get("product_id"),
    )
    try:
        await notify_managers(
            bot,
            settings.managers_chat_id,
            lead,
            data.get("product_title"),
        )
    except Exception:
        log.exception("Failed to notify managers chat")

    await state.clear()
    await call.answer()
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.message.answer(
        f"Спасибо! Заявка #{lead.id} принята.\n"
        "Менеджер свяжется в течение рабочего дня.",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(LeadForm.confirming, F.data == "lead_edit")
async def step_edit(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(LeadForm.waiting_name)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    data = await state.get_data()
    await call.message.answer(
        "Как к вам обращаться?",
        reply_markup=use_name_kb(data.get("name")),
    )


# ---------- managers: take in work ----------
@router.callback_query(F.data.startswith("lead_take:"))
async def take(call: CallbackQuery, session: AsyncSession):
    lead_id = int(call.data.split(":", 1)[1])

    if call.from_user.id not in settings.admin_ids:
        await call.answer("Только для менеджеров", show_alert=True)
        return

    admin = await session.get(Admin, call.from_user.id)
    if admin is None:
        admin = Admin(
            id=call.from_user.id,
            full_name=call.from_user.full_name or str(call.from_user.id),
            role=AdminRole.manager,
            is_active=True,
        )
        session.add(admin)
        await session.commit()

    lead = await take_lead(session, lead_id, call.from_user.id)
    if lead is None:
        await call.answer("Уже взяли", show_alert=True)
        return

    base_text = call.message.html_text or ""
    new_text = f"{base_text}\n\n✅ В работе: {call.from_user.full_name}"
    try:
        await call.message.edit_text(new_text, reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.answer("Взяли в работу")
