import pytest

from app.repositories.users import UserRepository


@pytest.mark.asyncio
async def test_success_wallet_transfer(client, test_db, user_factory, wallet_factory):
    """Test success wallet transfer."""

    user_repo = UserRepository(db=test_db)
    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    params = {
        "wallet_from": wallet_1.id,
        "wallet_to": wallet_2.id,
        "amount": 50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 200
    new_user_data_1 = await user_repo.get_by_id(user_id=base_user_1.id)
    new_user_data_2 = await user_repo.get_by_id(user_id=base_user_2.id)

    assert new_user_data_1.balance == 50
    assert new_user_data_2.balance == 150


@pytest.mark.asyncio
async def test_failed_wallet_transfer_amount_is_negative(
    client, test_db, user_factory, wallet_factory
):
    """Test failed wallet transfer (amount field is negative)."""

    user_repo = UserRepository(db=test_db)
    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    params = {
        "wallet_from": wallet_1.id,
        "wallet_to": wallet_2.id,
        "amount": -50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await user_repo.get_by_id(user_id=base_user_1.id)
    new_user_data_2 = await user_repo.get_by_id(user_id=base_user_2.id)

    assert new_user_data_1.balance == 100
    assert new_user_data_2.balance == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_params_are_empty(
    client, test_db, user_factory, wallet_factory
):
    """Test failed wallet transfer (amount field is negative)."""

    user_repo = UserRepository(db=test_db)
    base_user_1 = user_factory.create()
    wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_factory.create(user=base_user_2)

    params = {}
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await user_repo.get_by_id(user_id=base_user_1.id)
    new_user_data_2 = await user_repo.get_by_id(user_id=base_user_2.id)

    assert new_user_data_1.balance == 100
    assert new_user_data_2.balance == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_wallets_are_equal(
    client, test_db, user_factory, wallet_factory
):
    """Test failed wallet transfer (Wallets are equal)."""

    user_repo = UserRepository(db=test_db)
    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_factory.create(user=base_user_2)

    params = {
        "wallet_from": wallet_1.id,
        "wallet_to": wallet_1.id,
        "amount": 50,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 422
    new_user_data_1 = await user_repo.get_by_id(user_id=base_user_1.id)
    new_user_data_2 = await user_repo.get_by_id(user_id=base_user_2.id)

    assert new_user_data_1.balance == 100
    assert new_user_data_2.balance == 100


@pytest.mark.asyncio
async def test_failed_wallet_transfer_wallets_not_enough_resources(
    client, test_db, user_factory, wallet_factory
):
    """Test failed wallet transfer (Wallets are equal)."""

    user_repo = UserRepository(db=test_db)
    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    params = {
        "wallet_from": wallet_1.id,
        "wallet_to": wallet_2.id,
        "amount": 110,
    }
    response = await client.post("/api/wallets/transfer", json=params)

    assert response.status_code == 400
    new_user_data_1 = await user_repo.get_by_id(user_id=base_user_1.id)
    new_user_data_2 = await user_repo.get_by_id(user_id=base_user_2.id)

    assert new_user_data_1.balance == 100
    assert new_user_data_2.balance == 100
