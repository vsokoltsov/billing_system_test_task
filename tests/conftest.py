import asyncio
from decimal import Decimal
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from mock import AsyncMock

from app.adapters.sql.db import connect_db, disconnect_db, get_db
from app.adapters.sql.models import users, wallet_operations, wallets
from app.api import users_routes, wallets_routes
from app.entities.user import BaseUser
from app.entities.wallet import WalletEntity
# pylint: disable=no-name-in-module
from app.main import init_app
from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.usecases.user import UserUsecase
from app.usecases.wallet import WalletUsecase
from tests.factories import UserFactory, WalletFactory


@pytest.fixture(autouse=True)
async def prepare_db(test_db):
    """Delete previous records from database"""

    await test_db.execute(query=users.delete())
    await test_db.execute(query=wallets.delete())
    await test_db.execute(query=wallet_operations.delete())
    yield


@pytest.fixture(scope="module")
def event_loop():
    """Redefine event_loop for tests."""

    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Retrieve instance of test database."""

    _db = get_db()
    if not _db.is_connected:
        await _db.connect()
    yield _db
    if _db.is_connected:
        await _db.disconnect()


@pytest.fixture
def user_factory():
    """UserFactory as pytest factory"""

    return UserFactory


@pytest.fixture
def wallet_factory():
    """WalletFactory as pytest factory"""

    return WalletFactory


@pytest.fixture
async def fake_base_user(test_db) -> BaseUser:
    """Return BaseUser schema."""

    repository = UserRepository(db=test_db)
    user_id = await repository.create(email="example@mail.com")
    user_raw = await test_db.fetch_one(
        query="select id, email from users where id = :id", values={"id": user_id}
    )
    return BaseUser(**user_raw)


@pytest.fixture
async def fake_wallet(test_db, fake_base_user) -> WalletEntity:
    """Return wallet entitiy."""

    wallet_id = await test_db.execute(
        query="insert into wallets(user_id, balance) values(:user_id, :balance) returning id",
        values={"user_id": fake_base_user.id, "balance": Decimal("10.0")},
    )
    wallet_raw = await test_db.fetch_one(
        query="select id, user_id, balance, currency from wallets where id = :id",
        values={"id": wallet_id},
    )
    return WalletEntity(**wallet_raw)


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
async def client(test_db) -> AsyncGenerator:
    """Cleint fixture for API tests."""
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)
    user_usecase = UserUsecase(
        app_db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    wallet_usecase = WalletUsecase(
        app_db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    app = init_app(
        connect_db=connect_db,
        disconnect_db=disconnect_db,
        routes=[users_routes, wallets_routes],
        user_usecase=user_usecase,
        wallet_usecase=wallet_usecase,
    )
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client_data:
        yield client_data
