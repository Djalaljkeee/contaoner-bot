import logging

from maxapi import Router
from maxapi.context.base import BaseContext
from maxapi.types import Message
from maxapi.types.updates.bot_started import BotStarted
from maxapi.types.updates.message_created import MessageCreated
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.keyboards.main import main_menu_kb
from bot_max.services.leads import upsert_user

log = logging.getLogger(__name__)
router = Router()

_WELCOME = (
    "Добро пожаловать в бот компании Петрикс-Хоум!\n\n"
    "Мы производим модульные дома и офисы из морских контейнеров.\n"
    "Качественно, быстро, по доступным ценам.\n\n"
    "Выберите раздел меню:"
)


@router.bot_started.register
async def on_bot_started(event: BotStarted, session: AsyncSession):
    await upsert_user(
        session,
        user_id=event.user.user_id,
        username=event.user.username,
        full_name=event.user.full_name,
    )
    await event.send(text=_WELCOME, attachments=[main_menu_kb()])


@router.message_created.register
async def cmd_start(event: MessageCreated, context: BaseContext, session: AsyncSession):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if text not in ("/start", "start"):
        return

    await context.clear()
    sender = event.message.sender
    if sender:
        await upsert_user(
            session,
            user_id=sender.user_id,
            username=sender.username,
            full_name=sender.full_name,
        )
    await event.message.answer(text=_WELCOME, attachments=[main_menu_kb()])
