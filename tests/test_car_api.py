# tests/test_car_api.py
from models import Vehicle

BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}
CAR = {"car_no": "abc-123", "model": "Civic", "company": "Honda", "onground_km": 20000}


def auth(client, user_id="ihsan"):
    client.post("/create_account", json={**BODY, "user_id": user_id})
    token = client.post("/login_account", json={"user_id": user_id, "password": "12345678"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_cars_require_login(client):
    assert client.post("/cars", json=CAR).status_code in (401, 403)
    assert client.delete("/cars/ABC-123").status_code in (401, 403)
    assert client.put("/cars/ABC-123/km", json={"onground_km": 1}).status_code in (401, 403)


def test_add_car(client, db_session):
    h = auth(client)
    r = client.post("/cars", json=CAR, headers=h)

    assert r.status_code == 201
    assert r.json()["message"] == "Car added successfully."
    car = db_session.query(Vehicle).one()
    assert (car.car_no, car.model, car.onground_km, car.active_user) == ("ABC-123", "Civic", 20000, "ihsan")


def test_add_duplicate_car_returns_409(client):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)
    assert client.post("/cars", json=CAR, headers=h).status_code == 409


def test_add_car_rejects_bad_input(client):
    h = auth(client)
    assert client.post("/cars", json={**CAR, "onground_km": -5}, headers=h).status_code == 422
    assert client.post("/cars", json={**CAR, "model": "   "}, headers=h).status_code == 422


def test_delete_car(client, db_session):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)

    r = client.delete("/cars/abc-123", headers=h)
    assert r.status_code == 200
    assert db_session.query(Vehicle).count() == 0
    assert client.delete("/cars/ABC-123", headers=h).status_code == 404


def test_other_user_cannot_delete_or_update_my_car(client, db_session):
    h1, h2 = auth(client, "ali"), auth(client, "sara")
    client.post("/cars", json=CAR, headers=h1)

    assert client.delete("/cars/ABC-123", headers=h2).status_code == 404
    assert client.put("/cars/ABC-123/km", json={"onground_km": 30000}, headers=h2).status_code == 404
    assert db_session.query(Vehicle).one().onground_km == 20000


def test_update_km(client, db_session):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)

    r = client.put("/cars/abc-123/km", json={"onground_km": 21000}, headers=h)
    assert r.status_code == 200
    assert db_session.query(Vehicle).one().onground_km == 21000


def test_update_km_same_value_is_allowed(client):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)
    assert client.put("/cars/ABC-123/km", json={"onground_km": 20000}, headers=h).status_code == 200


def test_update_km_cannot_go_down(client, db_session):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)

    r = client.put("/cars/ABC-123/km", json={"onground_km": 19000}, headers=h)
    assert r.status_code == 400
    assert "20000" in r.json()["detail"]
    assert db_session.query(Vehicle).one().onground_km == 20000


def test_update_km_errors(client):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)
    assert client.put("/cars/NOPE/km", json={"onground_km": 5}, headers=h).status_code == 404
    assert client.put("/cars/ABC-123/km", json={"onground_km": -1}, headers=h).status_code == 422