from typing import Annotated
import wtforms

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import database, poasts

templates = Jinja2Templates(directory="templates")


class CreatePoastForm(wtforms.Form):
    poast_text = wtforms.TextAreaField("text", [wtforms.validators.DataRequired()])
    reply_to = wtforms.HiddenField("reply_to")
    submit = wtforms.SubmitField("Submit")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
@app.get("/index")
@app.get("/threads")
async def get_threads(request: Request) -> HTMLResponse:
    new_form = CreatePoastForm()
    new_form.reply_to.data = "Nobody"

    query = (
        poasts.select().where(poasts.c.reply_to == None).order_by(poasts.c.id.desc())
    )
    results = await database.fetch_all(query=query)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "poasts": results,
            "form": new_form,
        },
    )


@app.get("/poast")
async def redirect_to_index() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@app.post("/poast")
async def create_poast(
    poast_text: Annotated[str, Form()],
    reply_to: Annotated[str, Form()],
    request: Request,
) -> RedirectResponse:
    print(request)
    # insert the poast into the database
    if reply_to == "Nobody":
        reply_to = None
    query = poasts.insert().values(text=poast_text, reply_to=reply_to)
    await database.execute(query=query)
    return RedirectResponse(url="/", status_code=303)


@app.get("/poast/{poast_id}")
async def get_poast(poast_id: int, request: Request) -> HTMLResponse:
    # Get Poast and Replyguys
    poast_query = poasts.select().where(poasts.c.id == poast_id)
    replies_query = (
        poasts.select()
        .where(poasts.c.reply_to == poast_id)
        .order_by(poasts.c.id.desc())
    )
    the_poast = await database.fetch_one(query=poast_query)
    the_replies = await database.fetch_all(query=replies_query)
    # Prep form for new replyguy
    reply_form = CreatePoastForm()
    reply_form.reply_to.data = poast_id
    return templates.TemplateResponse(
        "thread.html",
        {
            "request": request,
            "poast": the_poast,
            "replies": the_replies,
            "form": reply_form,
        },
    )
