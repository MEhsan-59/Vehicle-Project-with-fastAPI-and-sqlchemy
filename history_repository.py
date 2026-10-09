# history_repository.py
from sqlalchemy.orm import Session

from models import History


class HistoryRepository:

    def __init__(self, database=Session):
        self.db = database

    def _newest_first(self, query):
        return query.order_by(History.action_timestamp.desc(), History.id.desc()).all()

    def get_all(self, active_user):
        return self._newest_first(
            self.db.query(History).filter(History.active_user == active_user))

    def get_by_car(self, car_no, active_user):
        return self._newest_first(
            self.db.query(History).filter(History.active_user == active_user,
                                          History.car_no == car_no))

    def get_by_part(self, part_name, active_user):
        return self._newest_first(
            self.db.query(History).filter(History.active_user == active_user,
                                          History.part_name == part_name))