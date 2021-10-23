import uvicorn
from fastapi import FastAPI, APIRouter
from typing import List

from app import settings
from app.api import users_routes, wallets_routes
from app.db import db
from databases import Database


def init_app(db: Database, routes: List[APIRouter]) -> FastAPI:
    """Initialize application parameters."""

    app = FastAPI(title="Billing system sample")
    app.add_event_handler("startup", db.connect)
    app.add_event_handler("shutdown", db.disconnect)
    for route in routes:
        app.include_router(route, prefix="/api")
    return app


def run_app():
    app = init_app(
        db=db,
        routes=[
            users_routes,
            wallets_routes
        ]
    )
    return app


if __name__ == "__main__":
    uvicorn.run(
        app="app.main:run_app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        loop="uvloop",
        reload=settings.APP_RELOAD,
        reload_dirs=settings.APP_HOME,
    )
