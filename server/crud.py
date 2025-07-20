from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from server.schema import Category, CategoryCreate


async def get_category_tree(session: AsyncSession):
    stmt = (
        select(Category)
        .where(Category.parent_id == None)
        .options(selectinload(Category.children))
    )
    result = await session.exec(stmt)
    return result.all()


async def get_category(session: AsyncSession, category_id: int):
    stmt = (
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.parent))
    )
    result = await session.exec(stmt)
    return result.one()


async def create_category(session: AsyncSession, category: CategoryCreate):
    category = Category.model_validate(category)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(session: AsyncSession, category_id: int, name: str):
    category = await session.get(Category, category_id)
    category.name = name
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category_id: int):
    category = await session.get(Category, category_id)
    await session.delete(category)
    await session.commit()
