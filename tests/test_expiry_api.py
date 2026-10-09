# tests/test_expiry_api.py
from datetime import date, timedelta
from types import SimpleNamespace

from models import Part, Maintenance, Vehicle
from expiry_service import ExpiryService

BODY = {"user_id": "ihsan", "user_name": "M. Ihsan", "password": "12345678"}
CAR = {"car_no": "abc-123", "model": "Civic", "company": "Honda", "onground_km": 20000}
TODAY = date(2024, 6, 1)


def auth(client, user_id="ihsan"):
    client.post("/create_account", json={**BODY, "user_id": user_id})
    token = client.post("/login_account", json={"user_id": user_id, "password": "12345678"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def detail(next_km=25000, next_date=TODAY + timedelta(days=100), km=20000, km_limit=200, day_limit=15):
    return SimpleNamespace(car_no="ABC-123", model="Civic", company="Honda", onground_km=km,
                           part_name="oil filter", km_limit=km_limit, day_limit=day_limit,
                           changed_km=18000, next_changed_km=next_km, changed_date=date(2024, 1, 1),
                           next_changed_date=next_date)


def add_record(db_session, car_no, part_name, next_km, next_date, user_id="ihsan"):
    car = db_session.query(Vehicle).filter(Vehicle.car_no == car_no, Vehicle.active_user == user_id).one()
    part = db_session.query(Part).filter(Part.part == part_name).first()
    if not part:
        part = Part(part=part_name, km_life=5000, month_life=6, km_limit=200, day_limit=15)
        db_session.add(part)
        db_session.flush()
    db_session.add(Maintenance(vehicle_id=car.id, part_id=part.id, changed_km=18000, next_changed_km=next_km,
                               changed_date=date(2024, 1, 1), next_changed_date=next_date))
    db_session.commit()


def test_ok_part_is_not_reported():
    assert ExpiryService(None).get_expiry_status(detail(), TODAY) is None


def test_expiring_by_km():
    s = ExpiryService(None).get_expiry_status(detail(next_km=20150), TODAY)
    assert s["status"] == "expiring"
    assert s["remaining_km"] == 150
    assert "150 km left" in s["message"]


def test_expiring_by_days():
    s = ExpiryService(None).get_expiry_status(detail(next_date=TODAY + timedelta(days=10)), TODAY)
    assert s["status"] == "expiring"
    assert s["remaining_days"] == 10


def test_limit_boundary_counts_as_expiring():
    assert ExpiryService(None).get_expiry_status(detail(next_km=20200), TODAY)["status"] == "expiring"
    assert ExpiryService(None).get_expiry_status(detail(next_km=20201), TODAY) is None


def test_expired_by_km():
    s = ExpiryService(None).get_expiry_status(detail(next_km=19900), TODAY)
    assert s["status"] == "expired"
    assert "100 km over" in s["message"]


def test_expired_when_exactly_due():
    assert ExpiryService(None).get_expiry_status(detail(next_km=20000), TODAY)["status"] == "expired"
    assert ExpiryService(None).get_expiry_status(detail(next_date=TODAY), TODAY)["status"] == "expired"


def test_expired_by_days():
    s = ExpiryService(None).get_expiry_status(detail(next_date=TODAY - timedelta(days=3)), TODAY)
    assert s["status"] == "expired"
    assert "3 days over" in s["message"]


def test_expiry_requires_login(client):
    assert client.get("/expiry").status_code in (401, 403)


def test_expiry_is_empty_with_no_data(client):
    h = auth(client)
    assert client.get("/expiry", headers=h).json() == []


def test_expiry_lists_expired_first(client, db_session):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)
    today = date.today()
    add_record(db_session, "ABC-123", "oil filter", 20100, today + timedelta(days=200))
    add_record(db_session, "ABC-123", "air filter", 25000, today + timedelta(days=200))
    add_record(db_session, "ABC-123", "brake pad", 19000, today + timedelta(days=200))

    result = client.get("/expiry", headers=h).json()

    assert [(r["part"], r["status"]) for r in result] == [("brake pad", "expired"), ("oil filter", "expiring")]
    assert result[0]["car_no"] == "ABC-123"
    assert result[0]["remaining_km"] == -1000


def test_expiry_shows_only_my_cars(client, db_session):
    h1, h2 = auth(client, "ali"), auth(client, "sara")
    client.post("/cars", json=CAR, headers=h1)
    add_record(db_session, "ABC-123", "oil filter", 19000, date.today() + timedelta(days=200), "ali")

    assert len(client.get("/expiry", headers=h1).json()) == 1
    assert client.get("/expiry", headers=h2).json() == []


def test_expiry_follows_km_update(client, db_session):
    h = auth(client)
    client.post("/cars", json=CAR, headers=h)
    add_record(db_session, "ABC-123", "oil filter", 25000, date.today() + timedelta(days=200))
    assert client.get("/expiry", headers=h).json() == []

    client.put("/cars/ABC-123/km", json={"onground_km": 24900}, headers=h)
    assert client.get("/expiry", headers=h).json()[0]["status"] == "expiring"