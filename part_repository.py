# part_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Part, Maintenance


class PartRepository:

    def __init__(self, database=Session):
        self.db = database

    def get_by_name(self, part_name):
        return self.db.query(Part).filter(Part.part == part_name).first()

    def get_all(self):
        return self.db.query(Part).order_by(Part.part).all()

    def create_part(self, part, km_life, month_life, km_limit, day_limit):
        part_config = Part(part=part, km_life=km_life, month_life=month_life,
                           km_limit=km_limit, day_limit=day_limit)
        try:
            self.db.add(part_config)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return None
        self.db.refresh(part_config)
        return part_config

    def update_part(self, part_config, km_life, month_life, km_limit, day_limit):
        part_config.km_life = km_life
        part_config.month_life = month_life
        part_config.km_limit = km_limit
        part_config.day_limit = day_limit
        self.db.commit()
        self.db.refresh(part_config)
        return part_config

    def count_usage(self, part_id):
        """How many maintenance records (on any car) use this part."""
        return self.db.query(Maintenance).filter(Maintenance.part_id == part_id).count()

    def delete_part(self, part_config):
        self.db.delete(part_config)
        self.db.commit()
