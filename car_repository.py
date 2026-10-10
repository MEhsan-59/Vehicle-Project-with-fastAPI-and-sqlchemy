# car_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Vehicle, Maintenance, History
from helper import Helper


class CarRepository:

    def __init__(self, database=Session):
        self.db = database

    def get_by_car_no(self, car_no, active_user):
        return (self.db.query(Vehicle)
                .filter(Vehicle.car_no == car_no, Vehicle.active_user == active_user)
                .first())

    def get_all(self, active_user):
        return (self.db.query(Vehicle)
                .filter(Vehicle.active_user == active_user)
                .order_by(Vehicle.car_no).all())

    def insert(self, vehicle):
        try:
            self.db.add(vehicle)
            self.db.flush()
            self.db.add(Helper.build_history(
                vehicle, "car_added", vehicle.active_user,
                details=f"{vehicle.company} {vehicle.model}, {vehicle.onground_km} km"))
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(vehicle)
        return vehicle

    def update_km(self, vehicle, old_km=None):
        if old_km is not None:
            self.db.add(Helper.build_history(
                vehicle, "km_updated", vehicle.active_user,
                details=f"km: {old_km} -> {vehicle.onground_km}"))
        self.db.commit()
        self.db.refresh(vehicle)

    def delete(self, vehicle):
        try:
            self.db.query(Maintenance).filter(Maintenance.vehicle_id == vehicle.id).delete()
            self.db.query(History).filter(History.vehicle_id == vehicle.id).delete()
            self.db.delete(vehicle)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise