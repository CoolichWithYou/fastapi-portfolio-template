import json
from typing import List, Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from sqlmodel.ext.asyncio.session import AsyncSession

from server import crud, redis_
from server.db import engine
from server.schema import Category, CategoryCreate, CategoryTree
from server.settings import Settings

settings = Settings()



async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


app = FastAPI()
templates = Jinja2Templates(directory="server/templates")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
async def index(
        request: Request,
        session: AsyncSession = Depends(get_session),
):
    cached = await redis_.redis_client.get('categories')
    if cached:
        raw_categories = json.loads(cached)
        categories = [CategoryTree(**item) for item in raw_categories]
    else:
        categories: List[CategoryTree] = await crud.get_categories_tree_orm(session)
        categories_json = json.dumps([cat.model_dump() for cat in categories])
        await redis_.redis_client.set('categories', categories_json)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories,
            "indent": Markup("&nbsp;&nbsp;&nbsp;&nbsp;"),
        },
    )


@app.post("/add")
async def add_category(
        name: str = Form(...),
        parent_id: Optional[str] = Form(None),
        session: AsyncSession = Depends(get_session),
):
    pid = int(parent_id) if parent_id else None

    category = CategoryCreate(name=name, parent_id=pid)
    await crud.create_category(session, category)
    return RedirectResponse("/", status_code=303)


@app.get("/category/{category_id}")
async def view_category(
        request: Request,
        category_id: int,
        session: AsyncSession = Depends(get_session),
):
    current_category = await session.get(Category, category_id)
    if not current_category:
        raise HTTPException(status_code=404)

    breadcrumbs = await crud.get_breadcrumbs(session, category_id)

    return templates.TemplateResponse(
        "category.html",
        {
            "request": request,
            "category": current_category,
            "breadcrumbs": breadcrumbs,
        },
    )


@app.post("/category/{category_id}/update")
async def update_category(
        category_id: int,
        name: str = Form(...),
        session: AsyncSession = Depends(get_session),
):
    await crud.update_category(session, category_id, name)
    return RedirectResponse(f"/category/{category_id}", status_code=303)


@app.post("/category/{category_id}/delete")
async def delete_category(
        category_id: int,
        session: AsyncSession = Depends(get_session),
):
    await crud.delete_category(session, category_id)
    return RedirectResponse("/", status_code=303)
