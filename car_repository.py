# car_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Vehicle, Maintenance, History


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
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(vehicle)
        return vehicle

    def update_km(self, vehicle):
        self.db.commit()
        self.db.refresh(vehicle)

    def delete(self, vehicle):
        self.db.query(Maintenance).filter(Maintenance.vehicle_id == vehicle.id).delete()
        self.db.query(History).filter(History.vehicle_id == vehicle.id).delete()
        self.db.delete(vehicle)
        self.db.commit()