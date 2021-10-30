from decimal import Decimal

import pytest


@pytest.mark.asyncio
async def test_success_user_creation(client):
    """Test success user creation."""

    res = await client.post("/api/users", json={"email": "example@mail.com"})
    assert res.status_code == 201
    assert res.json().get("email") == "example@mail.com"


@pytest.mark.asyncio
async def test_failed_user_creation_user_exists(client, user_factory):
    """Test failed user creation (user already exists)."""

    user = user_factory()

    res = await client.post("/api/users", json={"email": user.email})
    assert res.status_code == 400
    assert res.json().get("detail") == "User with this email already exists."


@pytest.mark.asyncio
async def test_failed_user_creation_email_is_empty(client):
    """Test failed user creation (email is empty)."""

    res = await client.post("/api/users", json={"email": ""})
    assert res.status_code == 422
    json_response = res.json()
    assert json_response["detail"][0]["type"] == "value_error.email"


@pytest.mark.asyncio
async def test_failed_user_creation_email_not_valid(client):
    """Test failed user creation (email is not valid)."""

    res = await client.post("/api/users", json={"email": "test"})
    assert res.status_code == 422
    json_response = res.json()
    assert json_response["detail"][0]["type"] == "value_error.email"


@pytest.mark.asyncio
async def test_success_user_enroll(client, wallet_factory):
    """Test success user money enroll."""

    wallet = wallet_factory.create()
    res = await client.put(f"/api/users/{wallet.user_id}/enroll", json={"amount": 10})
    assert res.status_code == 200
    json_response = res.json()
    assert json_response["balance"] == wallet.balance + Decimal("10.0")


@pytest.mark.asyncio
async def test_failed_user_enroll(client):
    """Test failed user money enroll (user does not exists)."""

    res = await client.put(f"/api/users/{1}/enroll", json={"amount": 10})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_failed_user_enroll_zero_amount(client, wallet_factory):
    """Test failed user money enroll (amount is zero)."""

    wallet = wallet_factory.create()
    res = await client.put(f"/api/users/{wallet.user_id}/enroll", json={"amount": 0})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_failed_user_enroll_no_wallet(client, user_factory):
    """Test failed user money enroll (user has no walled)."""

    user = user_factory.create()

    res = await client.put(f"/api/users/{user.id}/enroll", json={"amount": 10})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_failed_user_enroll_wrong_amount_type(client, wallet_factory):
    """Test failed user money enroll (wrong amount type)."""

    wallet = wallet_factory.create()

    res = await client.put(f"/api/users/{wallet.user_id}/enroll", json={"amount": "abc"})
    assert res.status_code == 422
