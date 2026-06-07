from maxapi.types import ButtonsPayload, CallbackButton

from max_bot.services.catalog import PROJECTS


def catalog_card_kb(project_index: int) -> ButtonsPayload:
    total = len(PROJECTS)
    nav_row = []
    if project_index > 0:
        nav_row.append(CallbackButton(text="◀ Назад", payload=f"catalog:show:{project_index - 1}"))
    if project_index < total - 1:
        nav_row.append(CallbackButton(text="Вперёд ▶", payload=f"catalog:show:{project_index + 1}"))

    buttons = []
    if nav_row:
        buttons.append(nav_row)

    buttons.append([
        CallbackButton(text="💰 Рассчитать стоимость", payload="menu:calc"),
        CallbackButton(text="📝 Заказать проект", payload="lead:catalog"),
    ])
    buttons.append([CallbackButton(text="⬅️ В главное меню", payload="menu:main")])
    return ButtonsPayload(buttons=buttons)


def catalog_list_kb() -> ButtonsPayload:
    rows = []
    for i, p in enumerate(PROJECTS):
        rows.append([CallbackButton(text=f"{p.title} — от {p.price:,} ₽".replace(",", " "), payload=f"catalog:show:{i}")])
    rows.append([CallbackButton(text="⬅️ В главное меню", payload="menu:main")])
    return ButtonsPayload(buttons=rows)
