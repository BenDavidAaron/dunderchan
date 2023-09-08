"""Dumbapp"""
import hashlib
from os import environ
from pathlib import Path
from typing import Optional
import socketio

import sqlalchemy
from databases import Database
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
htmx_init(templates=Jinja2Templates(directory=Path("app") / "templates"))

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

DATABASE_URL = environ.get("DUNDERCHAN_SQL_URL", "sqlite:///./test.db")
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

posts = sqlalchemy.Table(
    "poasts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author_hash", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=False),
)

metadata.create_all(engine)


def hash_author_id(author_id: str) -> str:
    """Hash author id for display"""
    hash_fxn = hashlib.md5()
    hash_fxn.update(author_id.encode("utf-8"))
    hash_value = hash_fxn.hexdigest()
    return hash_value[:6]


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    """Root page"""
    random_post = await database.fetch_one(posts.select().order_by(sqlalchemy.func.random()).limit(1))
    try:
        motd = random_post.title
    except Exception as exc:
        motd = str(exc)
    return {"greeting": motd}


@app.get("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def get_posts(request: Request):
    """Get posts"""
    del request
    query_statement = posts.select().order_by(posts.c.id.desc()).limit(50)
    posts_list = await database.fetch_all(query_statement)
    return {"posts": posts_list}


@app.post("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    author: Optional[str] = Form(None),
):
    """Create a new post"""
    if author is not None:
        author_hash = hash_author_id(author)
    else:
        author_hash = hash_author_id(request.client.host)

    insert_statement = posts.insert().values(
        title=title,
        content=content,
        author_hash=author_hash,
    )
    await database.execute(insert_statement)

    # Broadcast the new poast
    await sio.emit("new_post", {"title": title, "content": content, "author_hash": author_hash})

    query_statement = posts.select().order_by(posts.c.id.desc()).limit(10)
    posts_list = await database.fetch_all(query_statement)
    return {"posts": posts_list}
