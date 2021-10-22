import uvicorn
from fastapi import FastAPI

from app import settings
from app.api import users_routes, wallets_routes
from app.db import db

app = FastAPI(title="Billing system sample")

app.add_event_handler("startup", db.connect)
app.add_event_handler("shutdown", db.disconnect)

app.include_router(users_routes, prefix="/api")
app.include_router(wallets_routes, prefix="/api")

# @app.on_event("startup")
# async def startup():
#     """ Connect to the database. """

#     await db.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     """ Close connection to the database. """

#     await db.disconnect()

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        loop="uvloop",
        reload=settings.APP_RELOAD,
        reload_dirs=settings.APP_HOME,
    )
