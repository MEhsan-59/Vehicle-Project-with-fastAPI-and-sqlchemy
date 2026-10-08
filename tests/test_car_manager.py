# tests/test_car_manager.py
from models import Account


def make_user(db_session, user_id="ihsan"):
    db_session.add(Account(user_id=user_id, user_name=user_id, password="x"))
    db_session.commit()


def test_add_car(db_session, car_manager):
    make_user(db_session)
    status, msg = car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")

    assert status is True
    assert msg == "Car added successfully."
    assert car_manager.get_all_cars("ihsan")[0].car_no == "ABC-123"


def test_add_duplicate_car_rejected(db_session, car_manager):
    make_user(db_session)
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.add_car("ABC-123", "City", "Honda", 2000, "ihsan")

    assert status is False
    assert msg == "Car already exists."
    assert len(car_manager.get_all_cars("ihsan")) == 1


def test_same_car_no_for_other_user_rejected(db_session, car_manager):
    make_user(db_session, "ihsan")
    make_user(db_session, "ali")
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ali")

    assert status is False
    assert msg == "Car already exists."


def test_update_km(db_session, car_manager):
    make_user(db_session)
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.update_km("ABC-123", 1500, "ihsan")

    assert status is True
    assert msg == "Onground km updated successfully."
    assert car_manager.get_all_cars("ihsan")[0].onground_km == 1500


def test_update_km_same_value_allowed(db_session, car_manager):
    make_user(db_session)
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, _ = car_manager.update_km("ABC-123", 1000, "ihsan")

    assert status is True


def test_update_km_lower_rejected(db_session, car_manager):
    make_user(db_session)
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.update_km("ABC-123", 500, "ihsan")

    assert status is False
    assert msg == "Onground km must not be less than old km 1000."
    assert car_manager.get_all_cars("ihsan")[0].onground_km == 1000


def test_update_missing_car(car_manager):
    status, msg = car_manager.update_km("GHOST", 100, "ihsan")

    assert status is False
    assert msg == "Car not found."


def test_update_other_users_car_not_found(db_session, car_manager):
    make_user(db_session, "ihsan")
    make_user(db_session, "ali")
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.update_km("ABC-123", 2000, "ali")

    assert status is False
    assert msg == "Car not found."


def test_delete_car(db_session, car_manager):
    make_user(db_session)
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.delete_car("ABC-123", "ihsan")

    assert status is True
    assert msg == "Car deleted successfully."
    assert car_manager.get_all_cars("ihsan") == []


def test_delete_missing_car(car_manager):
    status, msg = car_manager.delete_car("GHOST", "ihsan")

    assert status is False
    assert msg == "Car not found."


def test_delete_other_users_car_not_found(db_session, car_manager):
    make_user(db_session, "ihsan")
    make_user(db_session, "ali")
    car_manager.add_car("ABC-123", "Civic", "Honda", 1000, "ihsan")
    status, msg = car_manager.delete_car("ABC-123", "ali")

    assert status is False
    assert msg == "Car not found."
    assert len(car_manager.get_all_cars("ihsan")) == 1