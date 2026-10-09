# maintenance_repository.py
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Maintenance, Vehicle, Part


class MaintenanceRepository:

    def __init__(self, database=Session):
        self.db = database

    def get_record(self, vehicle_id, part_id):
        return (self.db.query(Maintenance)
                .filter(Maintenance.vehicle_id == vehicle_id,
                        Maintenance.part_id == part_id)
                .first())

    def upsert(self, vehicle_id, part_id, changed_km, next_changed_km,
               changed_date, next_changed_date, history=None):
        values = dict(changed_km=changed_km, next_changed_km=next_changed_km,
                      changed_date=changed_date, next_changed_date=next_changed_date)
        record = self.get_record(vehicle_id, part_id)
        is_new = record is None

        try:
            if is_new:
                self.db.add(Maintenance(vehicle_id=vehicle_id, part_id=part_id, **values))
            else:
                for key, value in values.items():
                    setattr(record, key, value)
            if history is not None:
                history.action_type = "part_added" if is_new else "part_updated"
                self.db.add(history)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            record = self.get_record(vehicle_id, part_id)
            for key, value in values.items():
                setattr(record, key, value)
            if history is not None:
                history.action_type = "part_updated"
                self.db.add(history)
            self.db.commit()
            is_new = False
        return is_new

    def get_details(self, keyword, active_user):
        keyword = keyword.strip().lower()
        query = (self.db.query(
                    Vehicle.car_no, Vehicle.model, Vehicle.company, Vehicle.onground_km,
                    Part.part.label("part_name"), Part.km_limit, Part.day_limit,
                    Maintenance.changed_km, Maintenance.next_changed_km,
                    Maintenance.changed_date, Maintenance.next_changed_date)
                 .join(Maintenance, Maintenance.vehicle_id == Vehicle.id)
                 .join(Part, Part.id == Maintenance.part_id)
                 .filter(Vehicle.active_user == active_user))
        if keyword:
            query = query.filter(
                func.lower(Vehicle.car_no).contains(keyword, autoescape=True) |
                func.lower(Part.part).contains(keyword, autoescape=True))
        return query.order_by(Vehicle.car_no, Part.part).all()