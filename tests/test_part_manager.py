# tests/test_part_manager.py
from models import Account, Maintenance
from datetime import date


def test_add_part_config(part_manager):
    status, msg = part_manager.add_part_config("oil filter", 5000, 6, 200, 15)

    assert status is True
    assert msg == "Part added successfully."
    assert part_manager.part_exists("oil filter") is True
    assert part_manager.get_part_config("oil filter").km_life == 5000


def test_add_duplicate_part_rejected(part_manager):
    part_manager.add_part_config("oil filter", 5000, 6, 200, 15)
    status, msg = part_manager.add_part_config("oil filter", 7000, 8, 300, 20)

    assert status is False
    assert msg == "Part already exists."
    assert part_manager.get_part_config("oil filter").km_life == 5000


def test_update_part_config(part_manager):
    part_manager.add_part_config("oil filter", 5000, 6, 200, 15)
    status, msg = part_manager.update_part_config("oil filter", 7000, 8, 300, 20)

    config = part_manager.get_part_config("oil filter")
    assert status is True
    assert msg == "Part updated successfully."
    assert (config.km_life, config.month_life, config.km_limit, config.day_limit) == (7000, 8, 300, 20)
    assert len(part_manager.get_all_parts()) == 1


def test_update_missing_part(part_manager):
    status, msg = part_manager.update_part_config("ghost", 1, 1, 0, 0)

    assert status is False
    assert msg == "Part not found."


def test_delete_part_config(part_manager):
    part_manager.add_part_config("oil filter", 5000, 6, 200, 15)
    status, msg = part_manager.delete_part_config("oil filter")

    assert status is True
    assert msg == "Part deleted successfully."
    assert part_manager.part_exists("oil filter") is False


def test_delete_missing_part(part_manager):
    status, msg = part_manager.delete_part_config("ghost")

    assert status is False
    assert msg == "Part not found."


def test_delete_part_in_use_is_refused(db_session, part_manager):
    from models import Vehicle
    db_session.add(Account(user_id="ihsan", user_name="Ihsan", password="x"))
    db_session.commit()
    part_manager.add_part_config("oil filter", 5000, 6, 200, 15)
    car = Vehicle(car_no="ABC-123", model="Civic", company="Honda", onground_km=10000, active_user="ihsan")
    db_session.add(car)
    db_session.commit()
    part = part_manager.get_part_config("oil filter")
    db_session.add(Maintenance(vehicle_id=car.id, part_id=part.id, changed_km=9000, next_changed_km=14000,
                               changed_date=date(2026, 1, 31), next_changed_date=date(2026, 7, 31)))
    db_session.commit()

    status, msg = part_manager.delete_part_config("oil filter")

    assert status is False
    assert msg == "Part is in use by 1 record(s) and cannot be deleted."
    assert part_manager.part_exists("oil filter") is True


def test_get_part_config_not_found(part_manager):
    assert part_manager.get_part_config("brake pad") is None


def test_get_all_parts_sorted(part_manager):
    part_manager.add_part_config("tyre", 40000, 36, 500, 30)
    part_manager.add_part_config("brake pad", 3000, 4, 100, 10)

    assert [p.part for p in part_manager.get_all_parts()] == ["brake pad", "tyre"]
