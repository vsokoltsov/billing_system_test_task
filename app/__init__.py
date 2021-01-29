from fastapi import FastAPI

from app.api import users, wallet

app = FastAPI()
app.include_router(users.router)
app.include_router(wallet.router)