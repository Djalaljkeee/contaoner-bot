from maxapi import Dispatcher, Router
from maxapi.context import BaseContext
from maxapi.filters import F
from maxapi.filters.command import Command
from maxapi.filters.state import StateFilter
from maxapi.types import BotStarted, MessageCallback, MessageCreated

from max_bot.config import settings
from max_bot.keyboards.main import main_menu_kb

router = Router()

WELCOME_TEXT = (
    f"👋 Добро пожаловать в бот «{settings.company_name}»!\n\n"
    "🏠 Мы производим модульные дома и офисы из морских контейнеров "
    "под ключ — от 168 000 ₽.\n\n"
    "⚡ Срок изготовления от 7 дней · 🛡 Гарантия 12 мес. · 🚚 Доставка по всей России\n\n"
    "Выберите раздел ниже 👇"
)


@router.bot_started()
async def on_bot_started(event: BotStarted, context: BaseContext) -> None:
    await context.clear()
    await event.send(WELCOME_TEXT, attachments=[main_menu_kb().pack()])


@router.message_created(Command("start"), StateFilter("*"))
async def on_start_command(event: MessageCreated, context: BaseContext) -> None:
    await context.clear()
    await event.message.answer(WELCOME_TEXT, attachments=[main_menu_kb().pack()])


@router.message_callback(F.callback.payload == "menu:main")
async def on_main_menu_callback(event: MessageCallback, context: BaseContext) -> None:
    await context.clear()
    await event.edit(WELCOME_TEXT, attachments=[main_menu_kb().pack()])


def register(dp: Dispatcher) -> None:
    dp.include_routers(router)
