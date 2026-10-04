# tests/test_main.py
BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}


def _login_and_get_token(client, user_id="ihsan", password="12345678"):
    create = client.post("/create_account", json={"user_id": user_id, "user_name": "M. Ihsan", "password": password})
    assert create.status_code == 200, create.text

    login = client.post("/login_account", json={"user_id": user_id, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_create_account_success(client):
    response = client.post("/create_account", json=BODY)
    assert response.status_code == 200
    assert response.json()["status"] is True


def test_create_duplicate_account_returns_409(client):
    client.post("/create_account", json=BODY)
    response = client.post("/create_account", json=BODY)
    assert response.status_code == 409


def test_create_account_short_password_returns_422(client):
    response = client.post("/create_account", json={**BODY, "password": "123"})
    assert response.status_code == 422


def test_login_returns_token(client):
    token = _login_and_get_token(client)
    assert token


def test_login_wrong_password_returns_401(client):
    client.post("/create_account", json=BODY)
    response = client.post("/login_account", json={"user_id": "ihsan", "password": "wrongpass"})
    assert response.status_code == 401


def test_profile_without_token_is_rejected(client):
    response = client.get("/me")
    assert response.status_code in (401, 403)


def test_profile_with_token(client):
    token = _login_and_get_token(client)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["user_id"] == "ihsan"


def test_profile_with_bad_token_returns_401(client):
    response = client.get("/me", headers={"Authorization": "Bearer garbage"})
    assert response.status_code == 401
