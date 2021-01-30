import pytest

@pytest.mark.asyncio
async def test_success_user_creation(client):
    """ Test success user creation. """

    res = await client.post("/users", json={"email": "example@mail.com"})
    assert res.status_code == 201
    assert res.json().get('email') == "example@mail.com"

@pytest.mark.asyncio
async def test_failed_user_creation(client, test_db):
    """ Test failed user creation (user already exists). """

    query = "insert into users(email) values (:email)"
    values={'email': "example@mail.com"}
    await test_db.execute(query=query, values=values)

    res = await client.post("/users", json={"email": "example@mail.com"})
    assert res.status_code == 400
    assert res.json().get('detail') == 'User with this email already exists.'
