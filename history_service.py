# history_service.py
from logger_setup import logger


class HistoryService:

    def __init__(self, history_repo):
        self.history_repo = history_repo

    def get_history(self, filter_type, value, active_user):
        if filter_type == "car":
            rows = self.history_repo.get_by_car(value, active_user)
        elif filter_type == "part":
            rows = self.history_repo.get_by_part(value, active_user)
        else:
            rows = self.history_repo.get_all(active_user)
        logger.debug(f"History rows found: {len(rows)}")
        return rows