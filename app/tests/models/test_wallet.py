from decimal import Decimal

import pytest
import asyncpg

from app.db import db
from app.models.user import User
from app.models.wallet import InsufficientFundsException, Wallet
from app.models.wallet_operations import WalletOperation


@pytest.mark.asyncio
async def test_success_wallet_enroll():
    """ Test success wallet enroll. """

    user = await User.create("example@mail.com")
    balance = await Wallet.enroll(user.get("wallet_id"), 10)
    assert balance == Decimal(10)


@pytest.mark.asyncio
async def test_track_transaction_creation(test_db):
    """ Test success transaction creation on success enroll. """

    user = await User.create("example@mail.com")
    await Wallet.enroll(user.get("wallet_id"), 10)

    query = "select wallet_to, operation, amount from wallet_operations"
    data = await test_db.fetch_all(query)

    assert dict(data[0]).get("operation") == WalletOperation.CREATE
    assert dict(data[1]).get("operation") == WalletOperation.RECEIPT


@pytest.mark.asyncio
async def test_failed_wallet_enroll_with_negative_value():
    """ Test failed wallet enroll with negative value. """

    user = await User.create("example@mail.com")
    with pytest.raises(AssertionError):
        await Wallet.enroll(user.get("wallet_id"), -10)


@pytest.mark.asyncio
async def test_failed_wallet_enroll():
    """ Test failed wallet enroll (wallet does not exists). """

    balance = await Wallet.enroll(1, 10)
    assert balance is None


@pytest.mark.asyncio
async def test_failed_wallet_enroll_with_zero_value():
    """ Test failed wallet enroll (amount is 0). """

    user = await User.create("example@mail.com")
    with pytest.raises(AssertionError):
        await Wallet.enroll(user.get("wallet_id"), 0)


@pytest.mark.asyncio
async def test_failed_wallet_enroll_with_wrong_type():
    """ Test failed wallet enroll (amount has wrong type). """

    user = await User.create("example@mail.com")
    with pytest.raises(ValueError):
        await Wallet.enroll(user.get("wallet_id"), "abc")


@pytest.mark.asyncio
async def test_success_get_by_user_id():
    """
    Test success retrieving wallet by its id.
    """

    user = await User.create("example@mail.com")
    balance = await Wallet.get_by_user_id(user.get("id"))
    assert dict(balance).get("id") == user.get("wallet_id")


@pytest.mark.asyncio
async def test_failed_get_by_user_id():
    """
    Test failed retrieving wallet by its id (wallet does not exist).
    """

    balance = await Wallet.get_by_user_id(1)
    assert balance is None


@pytest.mark.asyncio
async def test_success_transfer_amount():
    """ Test success transfer among users' wallets. """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    wallet_from_id = await Wallet.transfer(
        user_data_1.get("wallet_id"), user_data_2.get("wallet_id"), 50
    )

    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert wallet_from_id == user_data_1.get("wallet_id")
    assert new_user_data_1.get("balance") == 50
    assert new_user_data_2.get("balance") == 150


@pytest.mark.asyncio
async def test_success_transfer_amount_transactions_creation(test_db):
    """ Test success transactions creations after transfer. """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    await Wallet.transfer(
        user_data_1.get("wallet_id"), user_data_2.get("wallet_id"), 50
    )

    query = (
        "select wallet_from, wallet_to, "
        "operation, amount, created_at "
        "from wallet_operations"
    )
    operations = await test_db.fetch_all(query)

    operations = [dict(op) for op in operations]
    moving_funds = [
        op
        for op in operations
        if op.get("operation") in (WalletOperation.RECEIPT, WalletOperation.DEBIT)
    ]

    debit = moving_funds[-2]
    receipt = moving_funds[-1]

    assert debit["operation"] == WalletOperation.DEBIT
    assert debit["wallet_from"] == user_data_1.get("wallet_id")
    assert debit["wallet_to"] == user_data_2.get("wallet_id")

    assert receipt["operation"] == WalletOperation.RECEIPT
    assert receipt["wallet_from"] == user_data_2.get("wallet_id")
    assert receipt["wallet_to"] == user_data_1.get("wallet_id")


@pytest.mark.asyncio
async def test_failed_transfer_amount_not_enough_resources():
    """
    Test failed transfer amoung
    users' wallets
    (Sorce wallet does not have
    enough resources).
    """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_2["balance"] = balance_2

    with pytest.raises(InsufficientFundsException):
        await Wallet.transfer(
            user_data_1.get("wallet_id"), user_data_2.get("wallet_id"), 50
        )

    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 0
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_transfer_amount_negative_value():
    """
    Test failed transfer amoung users' wallets (Funds has negative value).
    """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    with pytest.raises(AssertionError):
        await Wallet.transfer(
            user_data_1.get("wallet_id"), user_data_2.get("wallet_id"), -50
        )

    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 100
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_transfer_amount_wallets_are_equal():
    """
    Test failed transfer amoung users' wallets (wallets are equal).
    """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    with pytest.raises(AssertionError):
        await Wallet.transfer(
            user_data_1.get("wallet_id"), user_data_1.get("wallet_id"), 50
        )

    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 100
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_saving_of_negative_amount_value():
    """ Test failed saving of wallets negative value. """

    user_1 = await User.create("example_1@mail.com")
    query = f"update wallets set balance = -100 " f'where user_id={user_1.get("id")}'
    with pytest.raises(asyncpg.exceptions.CheckViolationError):
        await db.execute(query)
