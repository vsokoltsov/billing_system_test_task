from fastapi import APIRouter

from .api import users_routes, wallets_routes

api_router = APIRouter(prefix="/api")
api_router.include_router(users_routes)
api_router.include_router(wallets_routes)
