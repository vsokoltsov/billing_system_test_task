import pytest

@pytest.mark.asyncio
async def test_success_user_creation(client):
    """ Test success user creation. """

    res = await client.post("/api/users", json={"email": "example@mail.com"})
    assert res.status_code == 201
    assert res.json().get('email') == "example@mail.com"

@pytest.mark.asyncio
async def test_failed_user_creation_user_exists(client, test_db):
    """ Test failed user creation (user already exists). """

    query = "insert into users(email) values (:email)"
    values={'email': "example@mail.com"}
    await test_db.execute(query=query, values=values)

    res = await client.post("/api/users", json={"email": "example@mail.com"})
    assert res.status_code == 400
    assert res.json().get('detail') == 'User with this email already exists.'

@pytest.mark.asyncio
async def test_failed_user_creation_email_is_empty(client):
    """ Test failed user creation (email is empty). """

    res = await client.post("/api/users", json={"email": ""})
    assert res.status_code == 422
    json_response = res.json()
    assert json_response['detail'][0]['type'] == 'value_error.email'

@pytest.mark.asyncio
async def test_failed_user_creation_email_not_valid(client):
    """ Test failed user creation (email is not valid). """

    res = await client.post("/api/users", json={"email": "test"})
    assert res.status_code == 422
    json_response = res.json()
    assert json_response['detail'][0]['type'] == 'value_error.email'