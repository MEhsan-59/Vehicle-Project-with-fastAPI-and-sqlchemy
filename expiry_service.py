# expiry_service.py
from datetime import date


class ExpiryService:

    def __init__(self, maintenance_service):
        self.maintenance_service = maintenance_service

    def get_expiry_status(self, detail, today=None):
        today = today or date.today()
        remaining_km = detail.next_changed_km - detail.onground_km
        remaining_days = (detail.next_changed_date - today).days

        expired = remaining_km <= 0 or remaining_days <= 0
        expiring = remaining_km <= detail.km_limit or remaining_days <= detail.day_limit
        if not (expired or expiring):
            return None

        status = "expired" if expired else "expiring"
        km_text = f"{remaining_km} km left" if remaining_km > 0 else f"{-remaining_km} km over"
        day_text = f"{remaining_days} days left" if remaining_days > 0 else f"{-remaining_days} days over"
        return {
            "car_no": detail.car_no,
            "model": detail.model,
            "company": detail.company,
            "part": detail.part_name,
            "status": status,
            "remaining_km": remaining_km,
            "remaining_days": remaining_days,
            "next_changed_km": detail.next_changed_km,
            "next_changed_date": detail.next_changed_date,
            "message": f"{detail.car_no} - {detail.part_name} {status.upper()}: {km_text}, {day_text}",
        }

    def get_all_expiry(self, active_user, today=None):
        statuses = []
        for detail in self.maintenance_service.get_vehicle_details("", active_user):
            status = self.get_expiry_status(detail, today)
            if status:
                statuses.append(status)
        statuses.sort(key=lambda s: (s["status"] != "expired", s["remaining_days"], s["remaining_km"]))
        return statuses