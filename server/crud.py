import functools
from typing import List

from sqlalchemy import Integer, func, join, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import aliased
from sqlmodel.ext.asyncio.session import AsyncSession

from server import redis_
from server.schema import Category, CategoryCreate, CategoryTree


def delete_cache(func_):
    @functools.wraps(func_)
    async def wrapper(*args, **kwargs):
        result = await func_(*args, **kwargs)
        await redis_.redis_client.delete("categories")
        return result

    return wrapper


async def get_breadcrumbs(tree, category_id: int) -> List[Category]:
    by_id = {node.id: node for node in tree}

    breadcrumbs = []
    current = by_id.get(category_id)

    while current:
        breadcrumbs.append(current)
        current = by_id.get(current.parent_id)

    return list(reversed(breadcrumbs))


@delete_cache
async def create_category(
    session: AsyncSession,
    category: CategoryCreate,
):
    category = Category.model_validate(category)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_categories_tree_orm(
    session: AsyncSession,
) -> List[CategoryTree]:
    cte = (
        select(
            Category.id,
            Category.name,
            Category.parent_id,
            func.cast(0, Integer).label("level"),
            array([Category.id]).label("path"),
        )
        .where(Category.parent_id.is_(None))
        .cte(name="CategoryTree", recursive=True)
    )

    c = aliased(Category, name="c")
    ct = aliased(cte, name="ct")

    recursive_part = select(
        c.id,
        c.name,
        c.parent_id,
        (ct.c.level + 1).label("level"),
        ct.c.path.concat(array([c.id])).label("path"),
    ).select_from(join(c, ct, c.parent_id == ct.c.id))

    cte = cte.union_all(recursive_part)

    full_query = select(
        cte.c.id, cte.c.name, cte.c.parent_id, cte.c.level, cte.c.path
    ).order_by(cte.c.path)

    result = await session.exec(full_query)
    rows = result.all()

    return [
        CategoryTree(
            id=row.id,
            name=row.name,
            parent_id=row.parent_id,
            level=row.level,
        )
        for row in rows
    ]


@delete_cache
async def update_category(
    session: AsyncSession,
    category_id: int,
    name: str,
):
    category = await session.get(Category, category_id)
    category.name = name
    await session.commit()
    return category


@delete_cache
async def delete_category(session: AsyncSession, category_id: int):
    category = await session.get(Category, category_id)
    await session.delete(category)
    await session.commit()
