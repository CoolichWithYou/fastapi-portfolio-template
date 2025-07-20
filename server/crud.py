from typing import List

from sqlalchemy import func, Integer, join, String, literal_column
from sqlalchemy.orm import selectinload, aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from server.schema import Category, CategoryCreate, CategoryTree


async def get_category_tree(session: AsyncSession):
    stmt = (
        select(Category)
        .where(Category.parent_id == None)
        .options(selectinload(Category.children))
    )
    result = await session.exec(stmt)
    return result.all()


async def get_breadcrumbs(session: AsyncSession, category_id: int) -> List[Category]:
    cte = (
        select(
            Category.id,
            Category.name,
            Category.parent_id,
            func.cast(Category.id, String).label("path"),
            literal_column('0').label("level")
        )
        .where(Category.id == category_id)
        .cte(name="breadcrumbs", recursive=True)
    )

    cat_alias = aliased(Category, name="c")
    cte_alias = aliased(cte, name="b")

    recursive_part = (
        select(
            cat_alias.id,
            cat_alias.name,
            cat_alias.parent_id,
            func.concat(cte_alias.c.path, ',', cat_alias.id).label("path"),
            cte_alias.c.level + 1
        )
        .join(cte_alias, cat_alias.id == cte_alias.c.parent_id)
    )

    cte = cte.union_all(recursive_part)

    full_query = (
        select(cte.c.id, cte.c.name)
        .order_by(cte.c.level.desc())
    )

    result = await session.exec(full_query)
    return [Category(id=row.id, name=row.name) for row in result.all()]


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


from sqlalchemy.dialects.postgresql import array

async def get_categories_tree_orm(session: AsyncSession) -> List[CategoryTree]:
    cte = (
        select(
            Category.id,
            Category.name,
            Category.parent_id,
            func.cast(0, Integer).label("level"),
            array([Category.id]).label("path")
        )
        .where(Category.parent_id.is_(None))
        .cte(name="CategoryTree", recursive=True)
    )

    c = aliased(Category, name="c")
    ct = aliased(cte, name="ct")

    recursive_part = (
        select(
            c.id,
            c.name,
            c.parent_id,
            (ct.c.level + 1).label("level"),
            ct.c.path.concat(array([c.id])).label("path")
        )
        .select_from(join(c, ct, c.parent_id == ct.c.id))
    )

    cte = cte.union_all(recursive_part)

    full_query = (
        select(
            cte.c.id,
            cte.c.name,
            cte.c.parent_id,
            cte.c.level,
            cte.c.path
        )
        .order_by(cte.c.path)
    )

    result = await session.exec(full_query)
    rows = result.all()

    return [CategoryTree(
        id=row.id,
        name=row.name,
        parent_id=row.parent_id,
        level=row.level
    ) for row in rows]



async def update_category(session: AsyncSession, category_id: int, name: str):
    category = await session.get(Category, category_id)
    category.name = name
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category_id: int):
    category = await session.get(Category, category_id)
    await session.delete(category)
    await session.commit()
