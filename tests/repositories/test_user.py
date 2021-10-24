from decimal import Decimal

import pytest
from asyncpg.exceptions import UniqueViolationError

from app.entities.currency import CurrencyEnum
from app.repositories.users import UserRepository


@pytest.mark.asyncio
async def test_success_user_creation(test_db):
    """Test success user creation with User model."""

    users_count = await test_db.execute("select count(*) from users")
    repository = UserRepository(db=test_db)
    await repository.create("example@mail.com")
    new_users_count = await test_db.execute("select count(*) from users")
    assert new_users_count == users_count + 1


@pytest.mark.asyncio
async def test_failed_user_creation_user_exists(test_db, user_factory):
    """Test failed user creation (user already exists)"""

    repository = UserRepository(db=test_db)
    await user_factory.create(email="example@mail.com")

    with pytest.raises(UniqueViolationError):
        await repository.create("example@mail.com")


@pytest.mark.asyncio
async def test_failed_user_creation_email_empty(test_db):
    """Test failed user creation (email empty)"""

    repository = UserRepository(db=test_db)

    with pytest.raises(ValueError):
        await repository.create("")


@pytest.mark.asyncio
async def test_success_user_by_id_receiving(test_db, user_factory, wallet_factory):
    """Test success user receiving with user id"""

    repository = UserRepository(db=test_db)
    # user_id = await user_factory.create(email="example@mail.com")
    factory_user = await user_factory.create(email="example@mail.com")
    wallet = await wallet_factory.create(user_id=factory_user.id, balance=Decimal("100"))

    user = await repository.get_by_id(factory_user.id)
    assert user is not None
    assert user.id == factory_user.id
    assert wallet.id == user.wallet_id
    assert user.currency == CurrencyEnum.USD


@pytest.mark.asyncio
async def test_failed_user_by_id_receiving(test_db):
    """Test failed user receiving with user id (user does not exists)"""

    repository = UserRepository(db=test_db)
    user = await repository.get_by_id(1)
    assert user is None


@pytest.mark.asyncio
async def test_success_user_by_wallet_id_receiving(test_db):
    """Test success user receiving with wallet id"""

    repository = UserRepository(db=test_db)
    user_id = await repository.create("example@mail.com")
    query = "insert into wallets(user_id) values (:user_id) returning id"
    values = {"user_id": user_id}
    wallet_id = await test_db.execute(query=query, values=values)

    user = await repository.get_by_wallet_id(wallet_id=wallet_id)
    assert user is not None
    assert user.id == user_id
    assert wallet_id == user.wallet_id
    assert user.currency == CurrencyEnum.USD


@pytest.mark.asyncio
async def test_failed_user_by_wallet_id_receiving(test_db):
    """Test failed user receiving with wallet id (user does not exists)"""

    repository = UserRepository(db=test_db)

    user = await repository.get_by_wallet_id(wallet_id=1)
    assert user is None
