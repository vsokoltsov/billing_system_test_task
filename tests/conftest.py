import asyncio
from typing import AsyncGenerator

import factory

import pytest
from httpx import AsyncClient
from decimal import Decimal

import sqlalchemy
from app.adapters.sql.db import get_db, connect_db, disconnect_db

# pylint: disable=no-name-in-module
from app.main import init_app
from app.models.user import users
from app.models.wallet import CurrencyEnum, wallets
from app.models.wallet_operations import wallet_operations
from app.repositories.users import UserRepository
from app.entities.user import BaseUser
from app.entities.wallet import WalletEntity
from app.api import users_routes, wallets_routes
from tests.factories import UserFactory, WalletFactory


# class UserFactory(factory.Factory):
#         class Meta:
#             model = BaseUser

#         id = factory.Sequence(lambda n: n+1)
#         email =  factory.LazyAttribute(lambda obj: '%s@example.com' % obj.id)



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


# @pytest.fixture(scope="session", autouse=True)
# async def connect_to_db(test_db):
#     """Establish connection before tests and disconnect after test."""

#     await test_db.connect()
#     yield test_db
#     await test_db.disconnect()


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
def user_factory(test_db):

    return UserFactory

@pytest.fixture
def wallet_factory(test_db):
    return WalletFactory

@pytest.fixture
async def fake_base_user(test_db) -> BaseUser:
    """Return BaseUser schema."""

    repository = UserRepository(db=test_db)
    user_id = await repository.create(email="example@mail.com")
    user_raw = await test_db.fetch_one(
        query="select id, email from users where id = :id",
        values={'id': user_id}
    )
    return BaseUser(**user_raw)

@pytest.fixture
async def fake_wallet(test_db, fake_base_user) -> WalletEntity:
    """Return wallet entitiy."""

    wallet_id = await test_db.execute(
        query="insert into wallets(user_id, balance) values(:user_id, :balance) returning id",
        values={'user_id': fake_base_user.id, 'balance': Decimal('10.0')}
    )
    wallet_raw = await test_db.fetch_one(
        query="select id, user_id, balance, currency from wallets where id = :id",
        values={'id': wallet_id}
    )
    return WalletEntity(**wallet_raw)


@pytest.fixture
async def client() -> AsyncGenerator:
    """Cleint fixture for API tests."""
    app = init_app(
        db=get_db(),
        routes=[
            users_routes,
            wallets_routes
        ]
    )
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client_data:
        yield client_data
