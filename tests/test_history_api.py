# tests/test_history_api.py
from models import Part, History

BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}
CAR = {"car_no": "abc-123", "model": "Civic", "company": "Honda", "onground_km": 20000}


def auth(client, user_id="ihsan"):
    client.post("/create_account", json={**BODY, "user_id": user_id})
    token = client.post("/login_account", json={"user_id": user_id, "password": "12345678"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup(client, db_session, user_id="ihsan"):
    h = auth(client, user_id)
    if not db_session.query(Part).filter(Part.part == "oil filter").first():
        db_session.add(Part(part="oil filter", km_life=5000, month_life=6, km_limit=200, day_limit=15))
        db_session.add(Part(part="air filter", km_life=8000, month_life=12, km_limit=200, day_limit=15))
        db_session.commit()
    client.post("/cars", json=CAR, headers=h)
    return h


def put_part(client, h, part="oil filter", km=18000):
    return client.put(f"/cars/abc-123/parts/{part}", json={"changed_km": km, "changed_date": "2024-01-31"}, headers=h)


def test_history_requires_login(client):
    assert client.get("/history").status_code in (401, 403)


def test_history_is_empty_at_start(client):
    h = auth(client)
    assert client.get("/history", headers=h).json() == []


def test_add_car_is_saved_automatically(client, db_session):
    h = setup(client, db_session)
    rows = client.get("/history", headers=h).json()

    assert len(rows) == 1
    assert rows[0]["action_type"] == "car_added"
    assert rows[0]["car_no"] == "ABC-123"
    assert rows[0]["details"] == "Honda Civic, 20000 km"
    assert rows[0]["action_timestamp"] is not None


def test_duplicate_car_does_not_save_history(client, db_session):
    h = setup(client, db_session)
    client.post("/cars", json=CAR, headers=h)
    assert db_session.query(History).count() == 1


def test_km_update_is_saved_with_old_and_new_km(client, db_session):
    h = setup(client, db_session)
    client.put("/cars/ABC-123/km", json={"onground_km": 21000}, headers=h)

    rows = client.get("/history", headers=h).json()
    assert rows[0]["action_type"] == "km_updated"
    assert rows[0]["details"] == "km: 20000 -> 21000"


def test_rejected_km_update_saves_nothing(client, db_session):
    h = setup(client, db_session)
    client.put("/cars/ABC-123/km", json={"onground_km": 100}, headers=h)
    assert db_session.query(History).count() == 1


def test_part_add_and_update_are_saved(client, db_session):
    h = setup(client, db_session)
    put_part(client, h)
    put_part(client, h, km=19000)

    rows = client.get("/history", headers=h).json()
    assert [r["action_type"] for r in rows] == ["part_updated", "part_added", "car_added"]
    assert rows[1]["part_name"] == "oil filter"
    assert rows[1]["changed_km"] == 18000
    assert "Next KM: 23000" in rows[1]["details"]


def test_filter_by_car_and_part(client, db_session):
    h = setup(client, db_session)
    client.post("/cars", json={**CAR, "car_no": "xyz-999"}, headers=h)
    put_part(client, h)
    put_part(client, h, part="air filter")

    by_car = client.get("/history?filter_type=car&value=xyz-999", headers=h).json()
    assert [r["action_type"] for r in by_car] == ["car_added"]

    by_part = client.get("/history?filter_type=part&value=Oil Filter", headers=h).json()
    assert [r["part_name"] for r in by_part] == ["oil filter"]

def test_filter_needs_a_value_and_a_valid_type(client, db_session):
    h = setup(client, db_session)
    assert client.get("/history?filter_type=car", headers=h).status_code == 400
    assert client.get("/history?filter_type=part&value=%20", headers=h).status_code == 400
    assert client.get("/history?filter_type=bogus", headers=h).status_code == 422


def test_history_is_private_to_each_user(client, db_session):
    h1 = setup(client, db_session, "ali")
    h2 = auth(client, "sara")
    put_part(client, h1)

    assert len(client.get("/history", headers=h1).json()) == 2
    assert client.get("/history", headers=h2).json() == []


def test_history_is_removed_with_the_car(client, db_session):
    h = setup(client, db_session)
    put_part(client, h)
    client.delete("/cars/ABC-123", headers=h)
    assert client.get("/history", headers=h).json() == []