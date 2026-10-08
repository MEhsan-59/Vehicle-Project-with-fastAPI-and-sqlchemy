# tests/test_maintenance_api.py
from datetime import date, timedelta

from models import Part, Maintenance, History, Vehicle

BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}
CAR = {"car_no": "abc-123", "model": "Civic", "company": "Honda", "onground_km": 20000}


def auth(client, user_id="ihsan"):
    client.post("/create_account", json={**BODY, "user_id": user_id})
    token = client.post("/login_account", json={"user_id": user_id, "password": "12345678"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup(client, db_session, user_id="ihsan"):
    h = auth(client, user_id)
    db_session.add(Part(part="oil filter", km_life=5000, month_life=6, km_limit=200, day_limit=15))
    db_session.commit()
    client.post("/cars", json=CAR, headers=h)
    return h


def put(client, h, km=18000, d="2024-01-31", part="oil filter", car="abc-123"):
    return client.put(f"/cars/{car}/parts/{part}", json={"changed_km": km, "changed_date": d}, headers=h)


def test_update_part_requires_login(client):
    r = client.put("/cars/ABC-123/parts/x", json={"changed_km": 1, "changed_date": "2024-01-01"})
    assert r.status_code in (401, 403)


def test_update_part_adds_a_new_part(client, db_session):
    h = setup(client, db_session)
    r = put(client, h)

    assert r.status_code == 200
    assert r.json()["message"] == "oil filter updated successfully."
    m = db_session.query(Maintenance).one()
    assert m.changed_km == 18000
    assert m.next_changed_km == 23000
    assert m.next_changed_date == date(2024, 7, 31)


def test_update_part_updates_an_existing_part(client, db_session):
    h = setup(client, db_session)
    put(client, h, km=1000, d="2024-01-01")
    put(client, h, km=15000, d="2024-03-15")

    m = db_session.query(Maintenance).one()
    assert m.changed_km == 15000
    assert m.next_changed_km == 20000
    assert m.next_changed_date == date(2024, 9, 15)


def test_part_name_and_car_no_are_normalised(client, db_session):
    h = setup(client, db_session)
    assert put(client, h, part="Oil Filter", car="Abc-123").status_code == 200


def test_update_part_errors(client, db_session):
    h = setup(client, db_session)
    future = (date.today() + timedelta(days=3)).isoformat()

    assert put(client, h, car="NOPE").status_code == 404
    assert put(client, h, part="unknown").status_code == 404
    assert put(client, h, km=99999).status_code == 400
    assert put(client, h, d=future).status_code == 400
    assert put(client, h, km=-1).status_code == 422
    assert db_session.query(Maintenance).count() == 0


def test_other_user_cannot_touch_my_car(client, db_session):
    setup(client, db_session, "ali")
    h2 = auth(client, "sara")
    assert put(client, h2).status_code == 404
    assert db_session.query(Maintenance).count() == 0


def test_history_is_saved_with_the_part(client, db_session):
    h = setup(client, db_session)
    put(client, h)
    put(client, h)

    rows = db_session.query(History).order_by(History.id).all()
    assert [x.action_type for x in rows] == ["part_added", "part_updated"]
    assert rows[0].part_name == "oil filter"
    assert rows[0].active_user == "ihsan"
    assert "Next KM: 23000" in rows[0].details


def test_delete_car_also_removes_its_parts_and_history(client, db_session):
    h = setup(client, db_session)
    put(client, h)

    client.delete("/cars/ABC-123", headers=h)

    assert db_session.query(Vehicle).count() == 0
    assert db_session.query(Maintenance).count() == 0
    assert db_session.query(History).count() == 0
    assert db_session.query(Part).count() == 1