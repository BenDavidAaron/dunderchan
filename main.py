import os

import databases
import sqlalchemy
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# DATABASE_URL = os.environ.get("DUNDERCHAN_SQL_URL", "sqlite:///./test.db")
# database = databases.Database(DATABASE_URL)
# metadata = sqlalchemy.MetaData()
# poasts = sqlalchemy.Table(
#     "poasts",
#     metadata,
#     sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
#     sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
#     sqlalchemy.Column("author_ip", sqlalchemy.String, nullable=False),
#     sqlalchemy.Column("reply_to", sqlalchemy.Integer, nullable=True),
# )
# engine = sqlalchemy.create_engine(
#     DATABASE_URL, connect_args={"check_same_thread": False}
# )
# metadata.create_all(engine)

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

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/index")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "poasts": [_ for _  in database["poasts"].values()]
        }
    )

@app.get("/poast/{poast_id}")
async def poast(request: Request, poast_id: int) -> HTMLResponse:
    poasts = []
    poasts.append(database["poasts"].get(poast_id, None))
    for _, poast in database["poasts"].items():
        if poast["reply_to"] == poast_id:
            poasts.append(poast)
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "poasts": poasts
        }
    )