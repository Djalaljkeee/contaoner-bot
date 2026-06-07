import json

from sqlalchemy import select

from max_bot.db.base import SessionLocal
from max_bot.db.models import Lead


async def save_lead(
    user_id: int,
    chat_id: int | None,
    name: str,
    phone: str,
    calc_config: dict | None = None,
    source: str = "unknown",
) -> Lead:
    async with SessionLocal() as session:
        lead = Lead(
            user_id=user_id,
            chat_id=chat_id,
            name=name,
            phone=phone,
            calc_config=json.dumps(calc_config, ensure_ascii=False) if calc_config else None,
            source=source,
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
        return lead


async def get_leads(limit: int = 50) -> list[Lead]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Lead).order_by(Lead.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
