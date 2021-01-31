import pytest
from decimal import Decimal

import asyncpg

from app.models.user import User, users
from app.models.wallet import Wallet, wallets

@pytest.mark.asyncio
async def test_success_wallet_enroll(test_db):
    """ Test success wallet enroll. """

    user = await User.create("example@mail.com")
    balance = await Wallet.enroll(user.get('wallet_id'), 10)
    assert balance == Decimal(10)

@pytest.mark.asyncio
async def test_success_wallet_enroll_with_negative_value(test_db):
    """ Test success wallet enroll with negative value. """

    user = await User.create("example@mail.com")
    balance = await Wallet.enroll(user.get('wallet_id'), -10)
    assert balance == Decimal(-10)

@pytest.mark.asyncio
async def test_failed_wallet_enroll(test_db):
    """ Test failed wallet enroll (wallet does not exists). """

    balance = await Wallet.enroll(1, 10)
    assert balance is None
    

@pytest.mark.asyncio
async def test_failed_wallet_enroll_with_zero_value(test_db):
    """ Test failed wallet enroll (amount is 0). """

    user = await User.create("example@mail.com")
    with pytest.raises(AssertionError):
        await Wallet.enroll(user.get('wallet_id'), 0)

@pytest.mark.asyncio
async def test_failed_wallet_enroll_with_wrong_type(test_db):
    """ Test failed wallet enroll (amount has wrong type). """

    user = await User.create("example@mail.com")
    with pytest.raises(asyncpg.exceptions.DataError):
        await Wallet.enroll(user.get('wallet_id'), 'abc')

@pytest.mark.asyncio
async def test_success_get_by_user_id(test_db):
    """
    Test success retrieving wallet by its id.
    """

    user = await User.create("example@mail.com")
    balance = await Wallet.get_by_user_id(user.get('id'))
    assert dict(balance).get('id') == user.get('wallet_id')

@pytest.mark.asyncio
async def test_failed_get_by_user_id(test_db):
    """
    Test failed retrieving wallet by its id (wallet does not exist).
    """

    balance = await Wallet.get_by_user_id(1)
    assert balance is None

