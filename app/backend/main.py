import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from config import APP_NAME, STATIC_DIR
from database import init_db
from routers import api, pages

logger = logging.getLogger("enigma")

app = FastAPI(title=APP_NAME)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.middleware("http")
async def no_cache_html(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# Routers
app.include_router(pages.router)
app.include_router(api.router)


@app.on_event("startup")
async def startup():
    init_db()
