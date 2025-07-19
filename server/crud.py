from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from server.schema import Category, CategoryCreate, CategoryUpdate


async def get_category_tree(session: Session):
    stmt = (
        select(Category)
        .where(Category.parent_id == None)
        .options(selectinload(Category.children))
    )
    result = session.exec(stmt)
    return result.all()


async def get_category(session: Session, category_id: int):
    return session.get(Category, category_id)


async def create_category(session: Session, category: CategoryCreate):
    category = Category.model_validate(category)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


async def update_category(session: Session, category_id: int, name: str):
    category = session.get(Category, category_id)
    category.name = name
    session.commit()
    return category


async def delete_category(session: Session, category_id: int):
    category = session.get(Category, category_id)
    session.delete(category)
    session.commit()
