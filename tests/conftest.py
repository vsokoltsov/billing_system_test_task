import asyncio
from typing import AsyncGenerator

import pytest
from databases.core import Database
from httpx import AsyncClient
from mock import AsyncMock

from app.adapters.sql.db import connect_db, disconnect_db, get_db
from app.adapters.sql.models import users, wallet_operations, wallets
from app.adapters.sql.tx import SQLTransactionManager

# pylint: disable=no-name-in-module
from app.main import init_app
from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.transport.http import api_router
from app.usecases.user import UserUsecase
from app.usecases.wallet import WalletUsecase
from tests.factories import UserFactory, WalletFactory


@pytest.fixture(autouse=True)
async def prepare_db(test_db):
    """Delete previous records from database"""

    await test_db.execute(query="select pg_advisory_unlock_all()")

    await test_db.execute(query=users.delete())
    await test_db.execute(query=wallets.delete())
    await test_db.execute(query=wallet_operations.delete())

    # Unlock all advisory locks
    await test_db.execute(query="select pg_advisory_unlock_all()")

    yield


@pytest.fixture(scope="module")
def event_loop():
    """Redefine event_loop for tests."""

    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db_instance() -> Database:
    """Return instance of encoding.Database"""
    return get_db()


@pytest.fixture
async def test_db(test_db_instance):
    """Retrieve instance of test database."""

    if not test_db_instance.is_connected:
        await test_db_instance.connect()
    yield test_db_instance
    if test_db_instance.is_connected:
        await test_db_instance.disconnect()


@pytest.fixture
def user_factory():
    """UserFactory as pytest factory"""

    return UserFactory


@pytest.fixture
def wallet_factory():
    """WalletFactory as pytest factory"""

    return WalletFactory


@pytest.fixture
async def user_repository_mock() -> AsyncMock:
    """Returns mock for user operation's repository"""

    return AsyncMock()


@pytest.fixture
async def wallet_repository_mock() -> AsyncMock:
    """Returns mock for wallet's repository"""

    return AsyncMock()


@pytest.fixture
async def wallet_operation_repository_mock() -> AsyncMock:
    """Returns mock for wallet operation's repository"""

    return AsyncMock()


@pytest.fixture
async def client(test_db_instance) -> AsyncGenerator:
    """Client fixture for API tests."""

    test_db = test_db_instance
    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)
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
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client_data:
        yield client_data
