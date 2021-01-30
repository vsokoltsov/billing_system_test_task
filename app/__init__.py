from fastapi import FastAPI

from app.api import users, wallet
from app.db import db

app = FastAPI(title="Billing system sample")
app.include_router(users.router)
app.include_router(wallet.router)

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()