import logging
import re
from typing import Optional

from maxapi import Bot, Router
from maxapi.context.base import BaseContext
from maxapi.filters import Contact as ContactFilter
from maxapi.types.updates.message_callback import MessageCallback
from maxapi.types.updates.message_created import MessageCreated
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.config import max_settings
from bot_max.keyboards.lead import cancel_kb, confirm_kb, phone_request_kb
from bot_max.keyboards.main import LEAD_BTN, main_menu_kb
from bot_max.services.leads import create_lead, set_user_name, set_user_phone, take_lead, upsert_user
from bot_max.services.notifications import notify_manager
from bot_max.states.lead import MaxLeadForm

log = logging.getLogger(__name__)
router = Router()

_PHONE_RE = re.compile(r"[\d\+\-\(\)\s]{7,20}")


def _normalize_phone(raw: str) -> Optional[str]:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] == "8":
        digits = "7" + digits[1:]
    if len(digits) == 10:
        digits = "7" + digits
    if len(digits) == 11 and digits[0] == "7":
        return f"+{digits}"
    return None


async def _start_lead(
    target,
    context: BaseContext,
    session: AsyncSession,
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
    product_title: Optional[str] = None,
    calc_config=None,
) -> None:
    user = await upsert_user(session, user_id, username, full_name)
    await context.clear()
    await context.update_data(
        product_title=product_title,
        calc_config=calc_config,
        name=None,
        phone=None,
    )
    await context.set_state(MaxLeadForm.waiting_name)
    intro = (
        f"Заявка по проекту: {product_title}.\n"
        "Менеджер свяжется в рабочее время.\n\n"
        if product_title
        else "Оставьте заявку — менеджер свяжется в рабочее время.\n\n"
    )
    name_hint = f"Вас зовут «{user.full_name}»? Отправьте это имя или введите другое:" if user.full_name else "Как к вам обращаться?"
    await target.answer(
        text=f"{intro}{name_hint}",
        attachments=[cancel_kb()],
    )


# ─── Entry from menu button ───────────────────────────────────────────────────

@router.message_created.register
async def lead_from_menu(
    event: MessageCreated, context: BaseContext, session: AsyncSession
):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text != LEAD_BTN:
        return
    sender = event.message.sender
    await _start_lead(
        event.message,
        context,
        session,
        user_id=sender.user_id if sender else 0,
        username=sender.username if sender else None,
        full_name=sender.full_name if sender else None,
    )


# ─── Entry from product card ──────────────────────────────────────────────────

@router.message_callback.register
async def lead_from_product(
    event: MessageCallback, context: BaseContext, session: AsyncSession
):
    payload = event.callback.payload or ""
    if not payload.startswith("maxlead:prod:"):
        return
    try:
        product_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    from bot_max.services.catalog import get_product
    product = await get_product(session, product_id)
    product_title = product.title if product else None
    user = event.callback.user
    await event.ack()
    await _start_lead(
        event,
        context,
        session,
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        product_title=product_title,
    )


# ─── Cancel ───────────────────────────────────────────────────────────────────

@router.message_callback.register
async def cancel_lead(event: MessageCallback, context: BaseContext):
    if event.callback.payload != "maxlead:cancel":
        return
    await context.clear()
    await event.edit(
        text="Заявка отменена.",
        attachments=[main_menu_kb()],
    )
    await event.ack()


# ─── Step: name ───────────────────────────────────────────────────────────────

@router.message_created.register
async def step_name(
    event: MessageCreated, context: BaseContext, session: AsyncSession
):
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxLeadForm.waiting_name):
        return
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if not text or len(text) < 2 or len(text) > 80 or text.replace(" ", "").isdigit():
        await event.message.answer(text="Имя выглядит странно — попробуйте ещё раз.")
        return
    sender = event.message.sender
    if sender:
        await set_user_name(session, sender.user_id, text)
    await context.update_data(name=text)
    user = await session.get(
        __import__("bot_max.db.models", fromlist=["MaxUser"]).MaxUser,
        sender.user_id if sender else 0,
    )
    saved_phone = user.phone if user else None
    phone_hint = f"\n\nИспользовать сохранённый номер {saved_phone}? Или поделитесь другим." if saved_phone else ""
    await context.set_state(MaxLeadForm.waiting_phone)
    await event.message.answer(
        text=f"Оставьте номер — менеджер перезвонит.{phone_hint}",
        attachments=[phone_request_kb()],
    )


# ─── Step: phone (contact share) ─────────────────────────────────────────────

@router.message_created.register
async def step_phone_contact(
    event: MessageCreated, context: BaseContext, session: AsyncSession
):
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxLeadForm.waiting_phone):
        return
    if not event.message.body or not event.message.body.attachments:
        return
    # Find contact attachment
    contact_att = None
    for att in event.message.body.attachments:
        if hasattr(att, "payload") and hasattr(att.payload, "vcf_info"):
            contact_att = att
            break
    if not contact_att:
        return

    vcf = contact_att.payload.vcf
    phone_raw = vcf.phone if hasattr(vcf, "phone") and vcf.phone else ""
    phone = _normalize_phone(phone_raw) if phone_raw else None
    if not phone:
        await event.message.answer(text="Не удалось распознать номер из контакта. Введите вручную.")
        return
    await _on_phone_ok(event.message, context, session, phone, event.message.sender)


# ─── Step: phone (text) ───────────────────────────────────────────────────────

@router.message_created.register
async def step_phone_text(
    event: MessageCreated, context: BaseContext, session: AsyncSession
):
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxLeadForm.waiting_phone):
        return
    if not event.message.body:
        return
    text = (event.message.body.text or "").strip()
    if not text:
        return
    # Skip if it's not text (could be other attachment)
    phone = _normalize_phone(text)
    if not phone:
        await event.message.answer(
            text="Не распознал номер. Пример: +7 (965) 555-33-66.\nПопробуйте ещё раз."
        )
        return
    await _on_phone_ok(event.message, context, session, phone, event.message.sender)


async def _on_phone_ok(target, context: BaseContext, session: AsyncSession, phone: str, sender) -> None:
    if sender:
        await set_user_phone(session, sender.user_id, phone)
    await context.update_data(phone=phone)
    await context.set_state(MaxLeadForm.confirming)
    data = await context.get_data()
    parts = [
        "Проверьте заявку",
        "",
        f"Имя: {data.get('name', '—')}",
        f"Телефон: {phone}",
    ]
    if data.get("product_title"):
        parts.append(f"Проект: {data['product_title']}")
    if data.get("calc_config"):
        cfg = data["calc_config"]
        if isinstance(cfg, dict) and "total" in cfg:
            parts.append(f"Расчёт: итого {cfg['total']:,} ₽".replace(",", " "))
    parts += ["", "Отправляем?"]
    await target.answer(text="\n".join(parts), attachments=[confirm_kb()])


# ─── Step: confirm ────────────────────────────────────────────────────────────

@router.message_callback.register
async def step_send(
    event: MessageCallback, context: BaseContext, session: AsyncSession, bot: Bot
):
    if event.callback.payload != "maxlead:send":
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxLeadForm.confirming):
        await event.ack()
        return

    data = await context.get_data()
    user = event.callback.user

    lead = await create_lead(
        session,
        user_id=user.user_id,
        name=data.get("name") or user.full_name or str(user.user_id),
        phone=data.get("phone", ""),
        product_title=data.get("product_title"),
        calc_config=data.get("calc_config"),
    )
    await context.clear()

    await notify_manager(bot, max_settings.max_manager_id, lead)

    await event.edit(
        text=f"Спасибо! Заявка #{lead.id} принята.\nМенеджер свяжется в течение рабочего дня.",
        attachments=[main_menu_kb()],
    )
    await event.ack()


@router.message_callback.register
async def step_edit(event: MessageCallback, context: BaseContext):
    if event.callback.payload != "maxlead:edit":
        return
    raw_state = await context.get_state()
    if str(raw_state) != str(MaxLeadForm.confirming):
        await event.ack()
        return
    await context.set_state(MaxLeadForm.waiting_name)
    await event.edit(
        text="Как к вам обращаться?",
        attachments=[cancel_kb()],
    )
    await event.ack()


# ─── Manager: take lead ───────────────────────────────────────────────────────

@router.message_callback.register
async def take_lead_cb(event: MessageCallback, session: AsyncSession):
    payload = event.callback.payload or ""
    if not payload.startswith("maxlead:take:"):
        return
    try:
        lead_id = int(payload.split(":", 2)[2])
    except (ValueError, IndexError):
        await event.ack()
        return

    lead = await take_lead(session, lead_id)
    if lead is None:
        await event.ack(notification="Уже взяли")
        return

    manager = event.callback.user
    current_text = ""
    if event.message and event.message.body:
        current_text = event.message.body.text or ""
    new_text = f"{current_text}\n\n✅ В работе: {manager.full_name}"
    await event.edit(text=new_text, attachments=[])
    await event.ack(notification="Взяли в работу")
