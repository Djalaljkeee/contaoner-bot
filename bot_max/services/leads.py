from typing import Any, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.db.models import MaxLead, MaxLeadStatus, MaxUser


async def upsert_user(
    session: AsyncSession,
    user_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
) -> MaxUser:
    user = await session.get(MaxUser, user_id)
    if user is None:
        user = MaxUser(id=user_id, username=username, full_name=full_name)
        session.add(user)
    else:
        if username is not None:
            user.username = username
        if full_name and not user.full_name:
            user.full_name = full_name
    await session.commit()
    await session.refresh(user)
    return user


async def set_user_phone(session: AsyncSession, user_id: int, phone: str) -> None:
    user = await session.get(MaxUser, user_id)
    if user:
        user.phone = phone
        await session.commit()


async def set_user_name(session: AsyncSession, user_id: int, full_name: str) -> None:
    user = await session.get(MaxUser, user_id)
    if user:
        user.full_name = full_name
        await session.commit()


async def create_lead(
    session: AsyncSession,
    user_id: int,
    name: str,
    phone: str,
    product_title: Optional[str] = None,
    calc_config: Optional[Any] = None,
    message: Optional[str] = None,
) -> MaxLead:
    lead = MaxLead(
        user_id=user_id,
        name=name,
        phone=phone,
        product_title=product_title,
        calc_config=calc_config,
        message=message,
        status=MaxLeadStatus.new,
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def take_lead(
    session: AsyncSession, lead_id: int
) -> Optional[MaxLead]:
    result = await session.execute(
        update(MaxLead)
        .where(MaxLead.id == lead_id, MaxLead.status == MaxLeadStatus.new)
        .values(status=MaxLeadStatus.in_progress)
        .returning(MaxLead.id)
    )
    await session.commit()
    if result.first() is None:
        return None
    return await session.get(MaxLead, lead_id)
