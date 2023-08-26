import pathlib
from typing import Annotated
import wtforms

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

from app.models import database, posts


class CreatePoastForm(wtforms.Form):
    poast_text = wtforms.TextAreaField("text", [wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Submit")


app = FastAPI()
htmx_init(templates=Jinja2Templates(directory=pathlib.Path("templates")))
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request) -> HTMLResponse:
    recent_thread_query = posts.select().order_by(posts.c.id.desc()).limit(7)
    recent_threads = await database.fetch_all(query=recent_thread_query)
    return {
        "motd": "Hello World",
        "form": CreatePoastForm(),
        "threads": recent_threads,
    }


@app.get("/thread/{id}", response_class=HTMLResponse)
@htmx("thread", "thread")
async def thread_page(request: Request, id: int) -> HTMLResponse:
    thread_query = posts.select().where(posts.c.id == id)
    thread = await database.fetch_one(query=thread_query)
    return {
        "thread": thread,
        "form": CreatePoastForm(),
    }
