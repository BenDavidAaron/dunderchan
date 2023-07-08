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

database = {
    "poasts": {
        0: {"id": 0, "text": "test", "author_ip": "127.0.0.1", "reply_to": None},
        1: {"id": 1, "text": "testosterone", "author_ip": "127.0.0.1", "reply_to": 0},
        2: {"id": 2, "text": "bonk", "author_ip": "127.0.0.1", "reply_to": None},
        3: {"id": 3, "text": "donk", "author_ip": "127.0.0.1", "reply_to": 2},
        4: {"id": 4, "text": "exam", "author_ip": "127.0.0.1", "reply_to": 0},
        5: {"id": 5, "text": "test again", "author_ip": "127.0.0.1", "reply_to": None}
    }
}

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
poasts = sqlalchemy.Table(
    "poasts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("author_ip", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("reply_to", sqlalchemy.Integer, nullable=True),
)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
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
@app.get("/index")
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

@app.post("/poast")
async def create_poast(poast_text: Annotated[str, Form()], reply_to: Annotated[str, Form()], request: Request) -> RedirectResponse:
    print(request)
    poast_id = len(database["poasts"])
    new_poast= {
        "id": poast_id,
        "text": poast_text,
        "reply_to": reply_to,
        "author_ip": request.client
    }
    database["poasts"][poast_id] = new_poast
    return RedirectResponse(url="/", status_code=303)