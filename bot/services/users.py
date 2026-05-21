from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User


async def upsert_user(
    session: AsyncSession,
    tg_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
) -> User:
    user = await session.get(User, tg_id)
    if user is None:
        user = User(
            id=tg_id,
            username=username,
            full_name=full_name,
            phone=phone,
        )
        session.add(user)
    else:
        if username is not None:
            user.username = username
        if full_name and not user.full_name:
            user.full_name = full_name
        if phone:
            user.phone = phone
    await session.commit()
    await session.refresh(user)
    return user


async def set_user_phone(session: AsyncSession, tg_id: int, phone: str) -> None:
    user = await session.get(User, tg_id)
    if user:
        user.phone = phone
        await session.commit()


async def set_user_name(session: AsyncSession, tg_id: int, full_name: str) -> None:
    user = await session.get(User, tg_id)
    if user:
        user.full_name = full_name
        await session.commit()
