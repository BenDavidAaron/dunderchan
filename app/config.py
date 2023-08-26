import pathlib
from typing import Any

import fastapi
import pydantic_settings


APP_DIR = pathlib.Path(__file__).resolve().parent


class Settings(pydantic_settings.BaseSettings):
    APP_DIR: pathlib.Path = APP_DIR

    STATIC_DIR: pathlib.Path = APP_DIR / "static"
    TEMPLATE_DIR: pathlib.Path = APP_DIR / "templates"

    FASTAPI_PROPERTIES: dict[str, Any] = {
        "title": "Dunderchan",
        "description": "A stupid text message board",
        "version": "0.0.1",
        "default_response_class": fastapi.responses.HTMLResponse,
    }

    DISABLE_DOCS: bool = False

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        fastapi_kwargs = self.FASTAPI_PROPERTIES
        if self.DISABLE_DOCS:
            fastapi_kwargs["docs_url"] = None
            fastapi_kwargs["redoc_url"] = None
            fastapi_kwargs["openapi_url"] = None
            fastapi_kwargs["openapi_prefix"] = None
        return fastapi_kwargs
