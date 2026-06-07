from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_max.db.models import MaxProduct


async def list_products(session: AsyncSession) -> list[MaxProduct]:
    result = await session.execute(
        select(MaxProduct)
        .where(MaxProduct.is_active.is_(True))
        .order_by(MaxProduct.sort_order, MaxProduct.id)
    )
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Optional[MaxProduct]:
    result = await session.execute(
        select(MaxProduct).where(
            MaxProduct.id == product_id,
            MaxProduct.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()
