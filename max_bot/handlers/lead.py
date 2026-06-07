import json
import re

from maxapi import Dispatcher, Router
from maxapi.context import BaseContext
from maxapi.filters import F
from maxapi.filters.contact import Contact
from maxapi.filters.state import StateFilter
from maxapi.types import MessageCallback, MessageCreated
from maxapi.types.attachments.contact import Contact as ContactAttachment

from max_bot.keyboards.lead import after_lead_kb, confirm_lead_kb, request_contact_kb
from max_bot.keyboards.main import back_to_menu_kb
from max_bot.services.leads import save_lead
from max_bot.services.notifications import notify_manager
from max_bot.states.lead import LeadForm

router = Router()

_PHONE_RE = re.compile(r"[\d\+\(\)\-\s]{7,20}")


def _clean_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 7:
        return None
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return f"+{digits}" if not digits.startswith("+") else digits


async def _start_lead(event: MessageCallback, context: BaseContext, source: str) -> None:
    data = await context.get_data()
    calc_config = data.get("calc_config")
    await context.update_data(source=source, calc_config=calc_config)
    await context.set_state(LeadForm.waiting_name)
    await event.edit(
        "📝 Оставить заявку\n\n"
        "Шаг 1/2 — Введите ваше имя:",
        attachments=[back_to_menu_kb().pack()],
    )


@router.message_callback(F.callback.payload == "lead:start")
async def lead_from_menu(event: MessageCallback, context: BaseContext) -> None:
    await _start_lead(event, context, source="main_menu")


@router.message_callback(F.callback.payload == "lead:catalog")
async def lead_from_catalog(event: MessageCallback, context: BaseContext) -> None:
    await _start_lead(event, context, source="catalog")


@router.message_callback(F.callback.payload == "lead:calc")
async def lead_from_calc(event: MessageCallback, context: BaseContext) -> None:
    await _start_lead(event, context, source="calculator")


@router.message_created(StateFilter(LeadForm.waiting_name))
async def got_name(event: MessageCreated, context: BaseContext) -> None:
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if len(text) < 2:
        await event.message.answer(
            "⚠️ Имя слишком короткое. Введите ваше имя (минимум 2 символа):",
            attachments=[back_to_menu_kb().pack()],
        )
        return

    await context.update_data(name=text)
    await context.set_state(LeadForm.waiting_phone)
    await event.message.answer(
        f"✅ Имя: {text}\n\n"
        "Шаг 2/2 — Введите номер телефона или нажмите кнопку ниже:",
        attachments=[request_contact_kb().pack()],
    )


@router.message_created(Contact(), StateFilter(LeadForm.waiting_phone))
async def got_contact(
    event: MessageCreated,
    context: BaseContext,
    contact: ContactAttachment,
) -> None:
    vcf = contact.payload.vcf if contact.payload else None
    phone = (vcf.phone if vcf else None) or ""
    await _process_phone(event, context, phone)


@router.message_created(StateFilter(LeadForm.waiting_phone))
async def got_phone_text(event: MessageCreated, context: BaseContext) -> None:
    raw = (event.message.body.text or "").strip() if event.message.body else ""
    await _process_phone(event, context, raw)


async def _process_phone(
    event: MessageCreated, context: BaseContext, raw: str
) -> None:
    phone = _clean_phone(raw)
    if not phone:
        await event.message.answer(
            "⚠️ Не удалось распознать номер. Введите в формате +7XXXXXXXXXX или 8XXXXXXXXXX:",
            attachments=[request_contact_kb().pack()],
        )
        return

    data = await context.get_data()
    await context.update_data(phone=phone)
    await context.set_state(LeadForm.confirming)

    calc_cfg_raw = data.get("calc_config")
    calc_info = ""
    if calc_cfg_raw:
        try:
            cfg = json.loads(calc_cfg_raw)
            calc_info = (
                f"\n\n📐 Конфигурация:\n"
                f"  Размер: {cfg.get('size', '—')}\n"
                f"  Утепление: {cfg.get('insulation', '—')}\n"
                f"  Отделка: {cfg.get('finish', '—')}\n"
                f"  Опции: {', '.join(cfg.get('options', [])) or 'нет'}\n"
                f"  Итого: {cfg.get('total', 0):,} ₽".replace(",", " ")
            )
        except Exception:
            pass

    await event.message.answer(
        f"📋 Проверьте данные:\n\n"
        f"👤 Имя: {data.get('name', '—')}\n"
        f"📞 Телефон: {phone}"
        f"{calc_info}\n\n"
        "Нажмите «Подтвердить» для отправки заявки. "
        "Мы свяжемся с вами в течение 15 минут.\n\n"
        "⚠️ Нажимая «Подтвердить», вы соглашаетесь на обработку персональных данных "
        "(konteiner24.ru/page/privacy).",
        attachments=[confirm_lead_kb().pack()],
    )


@router.message_callback(
    F.callback.payload == "lead:confirm",
    states=[LeadForm.confirming],
)
async def confirm_lead(event: MessageCallback, context: BaseContext) -> None:
    data = await context.get_data()
    name = data.get("name", "—")
    phone = data.get("phone", "—")
    source = data.get("source", "unknown")
    calc_cfg_raw = data.get("calc_config")
    calc_cfg = json.loads(calc_cfg_raw) if calc_cfg_raw else None

    chat_id, user_id = event.get_ids()

    lead = await save_lead(
        user_id=user_id,
        chat_id=chat_id,
        name=name,
        phone=phone,
        calc_config=calc_cfg,
        source=source,
    )

    await context.clear()

    from max_bot.config import settings as cfg
    await event.edit(
        f"✅ Заявка #{lead.id} принята!\n\n"
        "Наш менеджер свяжется с вами в течение 15 минут.\n\n"
        f"📞 Если хотите позвонить сами: {cfg.company_phone}\n\n"
        "Спасибо, что выбрали Петрикс-Хоум! 🏠",
        attachments=[after_lead_kb().pack()],
    )

    if event.bot:
        await notify_manager(event.bot, lead)


def register(dp: Dispatcher) -> None:
    dp.include_routers(router)
