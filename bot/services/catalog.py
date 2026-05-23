from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import ContainerSpec, Product, ProductPhoto, ProductType


async def list_products(
    session: AsyncSession,
    product_type: ProductType,
    container_spec: Optional[ContainerSpec] = None,
) -> list[Product]:
    q = select(Product).where(
        Product.type == product_type,
        Product.is_active.is_(True),
    )
    if container_spec is not None:
        q = q.where(Product.container_spec == container_spec)
    q = q.order_by(Product.sort_order, Product.id)
    result = await session.execute(q)
    return list(result.scalars().all())


async def get_product_with_photos(
    session: AsyncSession, product_id: int
) -> Optional[Product]:
    result = await session.execute(
        select(Product)
        .options(selectinload(Product.photos))
        .where(Product.id == product_id, Product.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def cache_photo_file_id(
    session: AsyncSession, photo_id: int, file_id: str
) -> None:
    photo = await session.get(ProductPhoto, photo_id)
    if photo and not photo.file_id:
        photo.file_id = file_id
        await session.commit()
