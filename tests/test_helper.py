# tests/test_helper.py
from datetime import date
from types import SimpleNamespace

from helper import Helper


def test_normalizers():
    assert Helper.normalize_car_no("  abc-123 ") == "ABC-123"
    assert Helper.normalize_part("  Oil Filter ") == "oil filter"


def test_add_months():
    assert Helper.add_months(date(2024, 1, 15), 6) == date(2024, 7, 15)
    assert Helper.add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert Helper.add_months(date(2023, 1, 31), 1) == date(2023, 2, 28)
    assert Helper.add_months(date(2024, 11, 30), 3) == date(2025, 2, 28)


def test_build_history():
    car = SimpleNamespace(id=1, car_no="ABC-123")
    h = Helper.build_history(car, "part_added", "ihsan", "oil filter", 1, date(2024, 1, 1), "x")
    assert (h.action_type, h.car_no, h.vehicle_id, h.active_user) == ("part_added", "ABC-123", 1, "ihsan")