from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import Category, Product, ProductKind, ProductPhoto


async def list_active_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.id)
    )
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def list_products(
    session: AsyncSession,
    category_id: int,
    kind: ProductKind = ProductKind.model,
) -> list[Product]:
    result = await session.execute(
        select(Product)
        .where(
            Product.category_id == category_id,
            Product.kind == kind,
            Product.is_active.is_(True),
        )
        .order_by(Product.sort_order, Product.area_m2.asc(), Product.id)
    )
    return list(result.scalars().all())


async def get_product_with_photos(
    session: AsyncSession, product_id: int
) -> Product | None:
    result = await session.execute(
        select(Product)
        .options(selectinload(Product.photos), selectinload(Product.category))
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
