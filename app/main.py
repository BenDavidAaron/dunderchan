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

@app.get("/customers", response_class=HTMLResponse)
@htmx("customers")
async def get_customers(request: Request):
    """Get customers"""
    return {"customers": ["John Doe", "Jane Doe"]}