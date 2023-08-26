from fastapi import FastAPI

from app.config import Settings
from app.routes import router

settings = Settings()

def get_app() -> FastAPI:
    """FastAPI application factory with specified settings."""
    new_app = FastAPI(**settings.fastapi_kwargs)
    new_app.include_router(router)
    return new_app 

app = get_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, **settings.uvicorn_kwargs)