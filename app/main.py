from typing import Callable

import uvicorn
from fastapi import APIRouter, FastAPI

from app import settings
from app.adapters.sql.db import connect_db, disconnect_db, get_db
from app.adapters.sql.tx import SQLTransactionManager
from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.transport.http import api_router
from app.usecases.user import AbstractUserUsecase, UserUsecase
from app.usecases.wallet import AbstractWalletUsecase, WalletUsecase


def init_app(
    connect_db: Callable,
    disconnect_db: Callable,
    router: APIRouter,
    user_usecase: AbstractUserUsecase,
    wallet_usecase: AbstractWalletUsecase,
) -> FastAPI:
    """Initialize application parameters."""

    app = FastAPI(title="Billing system sample")
    app.add_event_handler("startup", connect_db)
    app.add_event_handler("shutdown", disconnect_db)
    app.include_router(router)
    app.state.user_usecase = user_usecase
    app.state.wallet_usecase = wallet_usecase
    return app


def run_app():
    """Run application instance"""

    _db = get_db()
    tx_manager = SQLTransactionManager(db=_db)
    user_repo = UserRepository(db=_db)
    wallet_repo = WalletRepository(db=_db)
    wallet_operation_repo = WalletOperationRepository(db=_db)
    user_usecase = UserUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    wallet_usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    app = init_app(
        connect_db=connect_db,
        disconnect_db=disconnect_db,
        router=api_router,
        user_usecase=user_usecase,
        wallet_usecase=wallet_usecase,
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
