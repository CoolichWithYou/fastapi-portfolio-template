import functools
import json
from typing import List

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


from sqlalchemy import text

async def get_categories_tree_orm(session: AsyncSession) -> List[CategoryTree]:
    raw_sql = text("""
        WITH RECURSIVE "CategoryTree"(id, name, parent_id, level, path) AS (
            SELECT
                id,
                name,
                parent_id,
                0 AS level,
                ARRAY[id] AS path
            FROM category
            WHERE parent_id IS NULL

            UNION ALL

            SELECT
                c.id,
                c.name,
                c.parent_id,
                ct.level + 1,
                ct.path || c.id
            FROM category c
            JOIN "CategoryTree" ct ON c.parent_id = ct.id
        )
        SELECT id, name, parent_id, level
        FROM "CategoryTree"
        ORDER BY path;
    """)

    result = await session.exec(raw_sql)
    rows = result.mappings().all()

    return [CategoryTree(**row) for row in rows]


async def get_categories_cached(session: AsyncSession) -> List[CategoryTree]:
    cached = await redis_.redis_client.get("categories")
    if cached:
        raw_categories = json.loads(cached)
        categories = [CategoryTree(**item) for item in raw_categories]
    else:
        categories = await get_categories_tree_orm(session)
        categories_json = json.dumps([cat.model_dump() for cat in categories])
        await redis_.redis_client.set("categories", categories_json)
    return categories


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
