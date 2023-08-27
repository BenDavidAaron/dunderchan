"""Dumbapp"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

app = FastAPI()
htmx_init(templates=Jinja2Templates(directory=Path("app") / "templates"))


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    """Root page"""
    return {"greeting": "Hello World"}


@app.get("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def get_posts(request: Request):
    """Get posts"""
    return {
        "posts": [
            {"id": 1, "title": "Post 1", "body": "Body 1"},
            {"id": 2, "title": "Post 2", "body": "Body 2"},
            {"id": 3, "title": "Post 3", "body": "Body 3"},
        ]
    }
