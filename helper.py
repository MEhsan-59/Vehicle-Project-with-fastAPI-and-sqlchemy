# helper.py
from models import History


class Helper:

    @staticmethod
    def normalize_car_no(car_no: str) -> str:
        return car_no.strip().upper()

    @staticmethod
    def normalize_part(part: str) -> str:
        return part.strip().lower()

    @staticmethod
    def add_months(date_obj, months: int):
        year = date_obj.year + (date_obj.month + months - 1) // 12
        month = (date_obj.month + months - 1) % 12 + 1
        day = date_obj.day
        while True:
            try:
                return date_obj.replace(year=year, month=month, day=day)
            except ValueError:
                day -= 1

    @staticmethod
    def build_history(car, action, user_id, part_name=None, changed_km=None,
                      changed_date=None, details=None) -> History:
        return History(vehicle_id=car.id, car_no=car.car_no, action_type=action,
                       part_name=part_name, changed_km=changed_km,
                       changed_date=changed_date, active_user=user_id,
                       details=details)