# maintenance_service.py
from datetime import date

from helper import Helper
from logger_setup import logger


class MaintenanceService:

    def __init__(self, car_repo, maintenance_repo, part_repo):
        self.car_repo = car_repo
        self.maintenance_repo = maintenance_repo
        self.part_repo = part_repo

    def update_part(self, car_no, part, new_change_km, new_change_date, active_user):
        vehicle = self.car_repo.get_by_car_no(car_no, active_user)
        if not vehicle:
            return False, "Car not found."

        part_config = self.part_repo.get_by_name(part)
        if not part_config:
            return False, "Part not found."

        if new_change_date > date.today():
            return False, "Future date not allowed."
        if new_change_km > vehicle.onground_km:
            return False, "New change km must be less than on ground km."

        next_km = new_change_km + part_config.km_life
        next_date = Helper.add_months(new_change_date, part_config.month_life)

        history = Helper.build_history(
            vehicle, "part_added", active_user, part, new_change_km, new_change_date,
            f"Next KM: {next_km}, Next Date: {next_date.isoformat()}")
        is_new = self.maintenance_repo.upsert(
            vehicle.id, part_config.id, new_change_km, next_km,
            new_change_date, next_date, history)

        logger.info(f"{part} {'added' if is_new else 'updated'} for {car_no}")
        return True, f"{part} updated successfully."

    def get_vehicle_details(self, keyword, active_user):
        results = self.maintenance_repo.get_details(keyword, active_user)
        logger.debug(f"Found {len(results)} rows for '{keyword}'")
        return results