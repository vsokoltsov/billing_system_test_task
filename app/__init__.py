from fastapi import FastAPI

from app.api import users, wallet
from app.db import db

app = FastAPI(title="Billing system sample")
app.include_router(users.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")

@app.on_event("startup")
async def startup():
    """ Connect to the database. """

    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    """ Close connection to the database. """

    await db.disconnect()
