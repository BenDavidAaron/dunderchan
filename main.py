import os
from typing import Annotated, Optional
import wtforms

import databases
import sqlalchemy
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

DATABASE_URL = os.environ.get("DUNDERCHAN_SQL_URL", "sqlite:///./test.db")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

poasts = sqlalchemy.Table(
    "poasts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("reply_to", sqlalchemy.Integer, nullable=True),
)

metadata.create_all(engine)

templates = Jinja2Templates(directory="templates")

class CreatePoastForm(wtforms.Form):
    poast_text = wtforms.StringField("text", [wtforms.validators.DataRequired()])
    reply_to = wtforms.HiddenField("reply_to")
    submit = wtforms.SubmitField("Submit")

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def get_threads(request: Request) -> HTMLResponse:
    new_form = CreatePoastForm()
    new_form.reply_to.data = 'Nobody'

    query = poasts.select()
    results = await database.fetch_all(query=query)

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "poasts": results,
            "form": new_form,
        }
    )

@app.get("/poast")
async def redirect_to_index() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@app.post("/poast")
async def create_poast(poast_text: Annotated[str, Form()], reply_to: Annotated[str, Form()], request: Request) -> RedirectResponse:
    print(request)
    # insert the poast into the database
    query = poasts.insert().values(text=poast_text, reply_to=reply_to)
    await database.execute(query=query)
    return RedirectResponse(url="/", status_code=303)


@app.get("/poast/{poast_id}")
async def get_poast(poast_id: int, request: Request) -> HTMLResponse:
    poast_query = poasts.select().where(poasts.c.id == poast_id)
    replies_query = poasts.select().where(poasts.c.reply_to == poast_id)
    the_poast = await database.fetch_one(query=poast_query)
    the_replies = await database.fetch_all(query=replies_query)
    print(the_poast)
    print(the_replies)
    return templates.TemplateResponse(
        "thread.html",
        {
            "request": request,
            "poast": the_poast,
            "replies": the_replies,
        },
    )