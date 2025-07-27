import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import markdown2
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from server import crud
from server.background import listen_notifications
from server.crud import get_categories_cached
from server.db import engine
from server.schema import Category, CategoryCreate
from server.settings import Settings

settings = Settings()


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(_: FastAPI):
    task_update = asyncio.create_task(listen_notifications())
    yield
    task_update.cancel()


app = FastAPI(lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=settings.STATIC_DIRECTORY),
    name="static",
)
templates = Jinja2Templates(directory="server/templates")


@app.get("/health")
def health():
    return {"status": "ok"}


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


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    categories = await get_categories_cached(session)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories,
            "indent": Markup("&nbsp;&nbsp;&nbsp;&nbsp;"),
        },
    )


@app.get("/category/{category_id}", response_class=HTMLResponse)
async def view_category(
    request: Request,
    category_id: int,
    session: AsyncSession = Depends(get_session),
):
    current_category = await session.get(Category, category_id)
    categories = await get_categories_cached(session)
    breadcrumbs = await crud.get_breadcrumbs(categories, category_id)
    if current_category.link:
        return RedirectResponse(current_category.link, status_code=303)
    if current_category.content:
        current_category.content = markdown2.markdown(
            current_category.content, extras=["fenced-code-blocks", "tables"]
        )
        return templates.TemplateResponse(
            "category.html",
            {
                "request": request,
                "category": current_category,
                "breadcrumbs": breadcrumbs,
            },
        )
    return RedirectResponse("/", status_code=303)


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
