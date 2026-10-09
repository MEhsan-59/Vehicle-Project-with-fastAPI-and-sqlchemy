# car_manager.py
from models import Vehicle
from logger_setup import logger


class CarManager:

    def __init__(self, car_repo):
        self.car_repo = car_repo

    def add_car(self, car_no, model, company, km, active_user):
        vehicle = Vehicle(car_no=car_no, model=model, company=company,
                          onground_km=km, active_user=active_user)
        if not self.car_repo.insert(vehicle):
            logger.debug(f"Duplicate car: {car_no}")
            return False, "Car already exists."
        logger.info(f"Car added: {car_no}")
        return True, "Car added successfully."

    def get_all_cars(self, active_user):
        return self.car_repo.get_all(active_user)

    def delete_car(self, car_no, active_user):
        vehicle = self.car_repo.get_by_car_no(car_no, active_user)
        if not vehicle:
            return False, "Car not found."

        self.car_repo.delete(vehicle)
        logger.info(f"Car deleted: {car_no}")
        return True, "Car deleted successfully."

    def update_km(self, car_no, km, active_user):
        vehicle = self.car_repo.get_by_car_no(car_no, active_user)
        if not vehicle:
            return False, "Car not found."
        if vehicle.onground_km > km:
            return False, f"Onground km must not be less than old km {vehicle.onground_km}."

        old_km = vehicle.onground_km
        vehicle.onground_km = km
        self.car_repo.update_km(vehicle, old_km)
        logger.info(f"KM updated for {car_no}: {old_km} -> {km}")
        return True, "Onground km updated successfully."