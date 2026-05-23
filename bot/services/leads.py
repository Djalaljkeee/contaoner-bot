from typing import Any, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Lead, LeadSource, LeadStatus, LeadType


async def create_lead(
    session: AsyncSession,
    user_id: int,
    name: str,
    phone: str,
    message: Optional[str],
    source: LeadSource,
    lead_type: LeadType = LeadType.regular,
    product_id: Optional[int] = None,
    calc_config: Optional[Any] = None,
) -> Lead:
    lead = Lead(
        user_id=user_id,
        product_id=product_id,
        type=lead_type,
        name=name,
        phone=phone,
        message=message,
        calc_config=calc_config,
        source=source,
        status=LeadStatus.new,
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def take_lead(
    session: AsyncSession, lead_id: int, manager_id: int
) -> Optional[Lead]:
    result = await session.execute(
        update(Lead)
        .where(Lead.id == lead_id, Lead.manager_id.is_(None))
        .values(manager_id=manager_id, status=LeadStatus.in_progress)
        .returning(Lead.id)
    )
    await session.commit()
    if result.first() is None:
        return None
    return await session.get(Lead, lead_id)
