import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_success_user_creation(client):
    """Test success user creation."""

    res = await client.post("/api/users", json={"email": "example@mail.com"})
    assert res.status_code == 201
    assert res.json().get("email") == "example@mail.com"


@pytest.mark.asyncio
async def test_failed_user_creation_user_exists(client, test_db):
    """Test failed user creation (user already exists)."""

    query = "insert into users(email) values (:email)"
    values = {"email": "example@mail.com"}
    await test_db.execute(query=query, values=values)

    res = await client.post("/api/users", json={"email": "example@mail.com"})
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
async def test_success_user_enroll(client):
    """Test success user money enroll."""

    user = await User.create("example@mail.com")
    res = await client.put(f'/api/users/{user["id"]}/enroll', json={"amount": 10})
    assert res.status_code == 200
    json_response = res.json()
    assert json_response["balance"] == 10


@pytest.mark.asyncio
async def test_failed_user_enroll(client):
    """Test failed user money enroll (user does not exists)."""

    res = await client.put(f"/api/users/{1}/enroll", json={"amount": 10})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_failed_user_enroll_zero_amount(client):
    """Test failed user money enroll (amount is zero)."""

    user = await User.create("example@mail.com")
    res = await client.put(f'/api/users/{user["id"]}/enroll', json={"amount": 0})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_failed_user_enroll_no_wallet(client, test_db):
    """Test failed user money enroll (user has no walled)."""

    query = "insert into users(email) values (:email)"
    values = {"email": "example@mail.com"}
    await test_db.execute(query=query, values=values)

    user_query = "select id, email from users where email = :email"
    user = await test_db.fetch_one(query=user_query, values=values)

    res = await client.put(f'/api/users/{user.get("id")}/enroll', json={"amount": 10})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_failed_user_enroll_wrong_amount_type(client):
    """Test failed user money enroll (wrong amount type)."""

    user = await User.create("example@mail.com")

    res = await client.put(
        f'/api/users/{user.get("id")}/enroll', json={"amount": "abc"}
    )
    assert res.status_code == 422
