"""Dumbapp"""
from os import environ
from pathlib import Path

import sqlalchemy
from databases import Database
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init
from pydantic import BaseModel

app = FastAPI()
htmx_init(templates=Jinja2Templates(directory=Path("app") / "templates"))

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
    sqlalchemy.Column("content", sqlalchemy.String, nullable=False),
)

metadata.create_all(engine)


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
    return {"greeting": "Dunderchan"}


class PostCreateSchema(BaseModel):
    title: str
    content: str


class PostSchema(PostCreateSchema):
    id: int


@app.get("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def get_posts(request: Request):
    """Get posts"""
    query_statement = posts.select().order_by(posts.c.id.desc()).limit(10)
    posts_list = await database.fetch_all(query_statement)
    return {"posts": posts_list}


@app.post("/posts", response_class=HTMLResponse)
@htmx("posts", "posts")
async def create_post(
    request: Request, title: str = Form(...), content: str = Form(...)
):
    """Create a new post"""
    del request
    insert_statement = posts.insert().values(
        title=title,
        content=content,
    )
    await database.execute(insert_statement)
    query_statement = posts.select().order_by(posts.c.id.desc()).limit(10)
    posts_list = await database.fetch_all(query_statement)
    return {"posts": posts_list}

@app.get("/thread/{id}", response_class=HTMLResponse)
@htmx("thread", "thread")
async def get_thread(request: Request, id: int):
    """Get thread"""
    op_query = posts.select().where(posts.c.id == id)
    op = await database.fetch_one(op_query)
    print(op)
    return {"op": op}