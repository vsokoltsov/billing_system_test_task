import pytest

from app.models.user import User
from app.models.wallet import Wallet


@pytest.mark.asyncio
async def test_success_wallet_transfer(client):
    """ Test success wallet transfer. """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    params = {
        "wallet_from": user_data_1.get("wallet_id"),
        "wallet_to": user_data_2.get("wallet_id"),
        "amount": 50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 200
    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 50
    assert new_user_data_2.get("balance") == 150


@pytest.mark.asyncio
async def test_failed_wallet_transfer_amount_is_negative(client):
    """ Test failed wallet transfer (amount field is negative). """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    params = {
        "wallet_from": user_data_1.get("wallet_id"),
        "wallet_to": user_data_2.get("wallet_id"),
        "amount": -50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 100
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_params_are_empty(client):
    """ Test failed wallet transfer (amount field is negative). """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    params = {}
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 100
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_wallets_are_equal(client):
    """ Test failed wallet transfer (Wallets are equal). """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_1 = await Wallet.enroll(user_1.get("wallet_id"), 100)
    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_1["balance"] = balance_1
    user_data_2["balance"] = balance_2

    params = {
        "wallet_from": user_data_1.get("wallet_id"),
        "wallet_to": user_data_1.get("wallet_id"),
        "amount": 50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 100
    assert new_user_data_2.get("balance") == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_wallets_not_enough_resources(client):
    """ Test failed wallet transfer (Wallets are equal). """

    user_1 = await User.create("example_1@mail.com")
    user_2 = await User.create("example_2@mail.com")

    balance_2 = await Wallet.enroll(user_2.get("wallet_id"), 100)

    user_data_1 = dict(user_1)
    user_data_2 = dict(user_2)

    user_data_2["balance"] = balance_2

    params = {
        "wallet_from": user_data_1.get("wallet_id"),
        "wallet_to": user_data_1.get("wallet_id"),
        "amount": 50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await User.get(user_data_1.get("id"))
    new_user_data_2 = await User.get(user_data_2.get("id"))

    assert new_user_data_1.get("balance") == 0
    assert new_user_data_2.get("balance") == 100
