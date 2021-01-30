import pytest
from decimal import Decimal

from asyncpg.exceptions import UniqueViolationError

from app.models.user import User, users

@pytest.mark.asyncio
async def test_success_user_creation(test_db):
    """ Test success user creation with User model. """

    users_count = await test_db.execute("select count(*) from users")
    await User.create("example@mail.com")
    new_users_count = await test_db.execute("select count(*) from users")
    assert new_users_count == users_count + 1

@pytest.mark.asyncio
async def test_success_wallet_creation(test_db):
    """ Test success wallet instance creation. """

    wallets_count = await test_db.execute("select count(*) from wallets")
    await User.create("example@mail.com")
    new_wallets_count = await test_db.execute("select count(*) from wallets")
    assert new_wallets_count == wallets_count + 1

@pytest.mark.asyncio
async def test_failed_user_creation_user_exists(test_db):
    """ Test failed user creation (user already exists). """

    query = "insert into users(email) values (:email)"
    values={'email': "example@mail.com"}
    await test_db.execute(query=query, values=values)


    with pytest.raises(UniqueViolationError):
        await User.create("example@mail.com")

@pytest.mark.asyncio
async def test_failed_user_creation_email_empty(test_db):
    """ Test failed user creation (email is empty). """

    with pytest.raises(AssertionError):
        await User.create("")

@pytest.mark.asyncio
async def test_success_get_user_creation(test_db):
    """ Test success user retrieving of user. """

    await User.create("example@mail.com")
    user = await User.get(1)
    assert user.get('email') == 'example@mail.com'
    assert user.get('balance') == Decimal(0)

@pytest.mark.asyncio
async def test_failed_retiriving_of_user():
    """ Test failed user retrieving (user does not exists). """

    user = await User.get(1)
    assert user == None