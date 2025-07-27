from typing import ForwardRef, List, Optional

from sqlmodel import Field, Relationship, SQLModel

CategoryRef = ForwardRef("Category")


class CategoryBase(SQLModel):
    name: str = Field(max_length=50)
    content: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)

    parent_id: Optional[int] = Field(
        default=None, foreign_key="category.id", index=True
    )


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    parent: Optional[CategoryRef] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"},
    )
    children: List[CategoryRef] = Relationship(
        back_populates="parent", cascade_delete=True
    )


class CategoryTree(SQLModel):
    id: int

    name: str
    level: int
    parent_id: Optional[int] = Field(
        default=None, foreign_key="category.id", index=True
    )


class CategoryUpdate(CategoryBase):
    id: Optional[int] = Field(default=None, foreign_key="category.id")
    name: str = Field(max_length=40)


class CategoryCreate(CategoryBase):
    pass
