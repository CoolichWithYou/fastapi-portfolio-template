from typing import Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession

from server import crud
from server.db import engine
from server.schema import CategoryCreate
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
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    categories = await crud.get_category_tree(session)
    return templates.TemplateResponse(
        "index.html", {"request": request, "categories": categories}
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
    request: Request, category_id: int, session: AsyncSession = Depends(get_session)
):
    category = await crud.get_category(session, category_id)
    breadcrumbs = []
    current = category
    while current:
        breadcrumbs.insert(0, current)
        current = current.parent
    return templates.TemplateResponse(
        "category.html",
        {"request": request, "category": category, "breadcrumbs": breadcrumbs},
    )


@app.post("/category/{category_id}/update")
async def update_category(
    category_id: int, name: str = Form(...), session: AsyncSession = Depends(get_session)
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
