import pytest
from decimal import Decimal

import asyncpg

from app.models.user import User, users
from app.models.wallet import Wallet, wallets, InsufficientFundsException

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


@pytest.mark.asyncio
async def test_success_transfer_amount(test_db):
    """ Test success transfer among users' wallets. """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get('wallet_id'), 100)
    balance_2 = await Wallet.enroll(user_2.get('wallet_id'), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1['balance'] = balance_1
    user_data_2['balance'] = balance_2

    await Wallet.transfer(user_data_1.get('wallet_id'), user_data_2.get('wallet_id'), 50)

    new_user_data_1 = await User.get(user_data_1.get('id'))
    new_user_data_2 = await User.get(user_data_2.get('id'))

    assert new_user_data_1.get('balance') == 50
    assert new_user_data_2.get('balance') == 150


@pytest.mark.asyncio
async def test_failed_transfer_amount_not_enough_resources(test_db):
    """ Test failed transfer amoung users' wallets (Soruce wallet does not have enough resources). """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_2 = await Wallet.enroll(user_2.get('wallet_id'), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_2['balance'] = balance_2

    with pytest.raises(InsufficientFundsException):
        await Wallet.transfer(user_data_1.get('wallet_id'), user_data_2.get('wallet_id'), 50)

    new_user_data_1 = await User.get(user_data_1.get('id'))
    new_user_data_2 = await User.get(user_data_2.get('id'))

    assert new_user_data_1.get('balance') == 0
    assert new_user_data_2.get('balance') == 100


@pytest.mark.asyncio
async def test_failed_transfer_amount_negative_value(test_db):
    """
    Test failed transfer amoung users' wallets (Funds has negative value).
    """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get('wallet_id'), 100)
    balance_2 = await Wallet.enroll(user_2.get('wallet_id'), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1['balance'] = balance_1
    user_data_2['balance'] = balance_2

    with pytest.raises(AssertionError):
        await Wallet.transfer(user_data_1.get('wallet_id'), user_data_2.get('wallet_id'), -50)

    new_user_data_1 = await User.get(user_data_1.get('id'))
    new_user_data_2 = await User.get(user_data_2.get('id'))

    assert new_user_data_1.get('balance') == 100
    assert new_user_data_2.get('balance') == 100


@pytest.mark.asyncio
async def test_failed_transfer_amount_wallets_are_equal(test_db):
    """
    Test failed transfer amoung users' wallets (wallets are equal).
    """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get('wallet_id'), 100)
    balance_2 = await Wallet.enroll(user_2.get('wallet_id'), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1['balance'] = balance_1
    user_data_2['balance'] = balance_2

    with pytest.raises(AssertionError):
        await Wallet.transfer(user_data_1.get('wallet_id'), user_data_1.get('wallet_id'), 50)

    new_user_data_1 = await User.get(user_data_1.get('id'))
    new_user_data_2 = await User.get(user_data_2.get('id'))

    assert new_user_data_1.get('balance') == 100
    assert new_user_data_2.get('balance') == 100