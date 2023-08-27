"""Dumbapp"""
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init
from pydantic import BaseModel

app = FastAPI()
htmx_init(templates=Jinja2Templates(directory=Path("app") / "templates"))

data = {"posts": []}


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    """Root page"""
    return {"greeting": "Hello World"}


class PostCreateSchema(BaseModel):
    title: str
    content: str


class PostSchema(PostCreateSchema):
    id: int


@app.get("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def get_posts(request: Request):
    """Get posts"""
    return data


@app.post("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def create_post(
    request: Request, title: str = Form(...), content: str = Form(...)
):
    """Create a new post"""
    new_post = {"id": len(data["posts"]) + 1, "title": title, "content": content}
    data["posts"].append(new_post)
    return data
