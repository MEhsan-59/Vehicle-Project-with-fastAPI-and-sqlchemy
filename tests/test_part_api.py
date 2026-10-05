# tests/test_part_api.py
BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}
PART = {"part": "oil filter", "km_life": 5000, "month_life": 6, "km_limit": 200, "day_limit": 15}
NEW_VALUES = {"km_life": 7000, "month_life": 8, "km_limit": 300, "day_limit": 20}


def auth(client, user_id="ihsan"):
    client.post("/create_account", json={**BODY, "user_id": user_id})
    token = client.post("/login_account", json={"user_id": user_id, "password": "12345678"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_parts_require_login(client):
    assert client.post("/parts", json=PART).status_code in (401, 403)
    assert client.put("/parts/oil filter", json=NEW_VALUES).status_code in (401, 403)
    assert client.delete("/parts/oil filter").status_code in (401, 403)
    assert client.get("/parts").status_code in (401, 403)


# ---------- add ----------
def test_add_part(client):
    h = auth(client)
    r = client.post("/parts", json=PART, headers=h)

    assert r.status_code == 201
    assert r.json()["message"] == "Part added successfully."
    assert client.get("/parts", headers=h).json()[0]["part"] == "oil filter"


def test_add_duplicate_part_returns_409(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    assert client.post("/parts", json=PART, headers=h).status_code == 409


def test_part_name_is_normalised(client):
    h = auth(client)
    client.post("/parts", json={**PART, "part": "  Oil Filter "}, headers=h)
    assert client.get("/parts", headers=h).json()[0]["part"] == "oil filter"
    assert client.post("/parts", json=PART, headers=h).status_code == 409


def test_add_part_invalid_values_return_422(client):
    h = auth(client)
    assert client.post("/parts", json={**PART, "km_life": 0}, headers=h).status_code == 422
    assert client.post("/parts", json={**PART, "month_life": -1}, headers=h).status_code == 422
    assert client.post("/parts", json={**PART, "km_limit": -5}, headers=h).status_code == 422
    assert client.post("/parts", json={**PART, "part": "   "}, headers=h).status_code == 422


# ---------- update ----------
def test_update_part(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    r = client.put("/parts/oil filter", json=NEW_VALUES, headers=h)

    assert r.status_code == 200
    assert r.json()["message"] == "Part updated successfully."
    part = client.get("/parts", headers=h).json()[0]
    assert (part["km_life"], part["month_life"], part["km_limit"], part["day_limit"]) == (7000, 8, 300, 20)


def test_update_part_name_in_url_is_normalised(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    assert client.put("/parts/Oil Filter", json=NEW_VALUES, headers=h).status_code == 200


def test_update_missing_part_returns_404(client):
    h = auth(client)
    assert client.put("/parts/ghost", json=NEW_VALUES, headers=h).status_code == 404


def test_update_part_invalid_values_return_422(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    assert client.put("/parts/oil filter", json={**NEW_VALUES, "km_life": 0}, headers=h).status_code == 422


# ---------- delete ----------
def test_delete_part(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    r = client.delete("/parts/oil filter", headers=h)

    assert r.status_code == 200
    assert r.json()["message"] == "Part deleted successfully."
    assert client.get("/parts", headers=h).json() == []


def test_delete_missing_part_returns_404(client):
    h = auth(client)
    assert client.delete("/parts/ghost", headers=h).status_code == 404


def test_part_can_be_added_again_after_delete(client):
    h = auth(client)
    client.post("/parts", json=PART, headers=h)
    client.delete("/parts/oil filter", headers=h)
    assert client.post("/parts", json=PART, headers=h).status_code == 201
