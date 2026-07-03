from db.models.statuses import Statuses
from .utils.service import BaseService


class StatusService(BaseService):
    def get_status(self, status_id: int):
        return self.get_by_id(Statuses, status_id)

    def list_statuses_by_status_set(self, status_set_id: int):
        return self.db.query(Statuses).filter(
            Statuses.status_set_id == status_set_id
        ).all()

    def list_all_statuses(self):
        return self.db.query(Statuses).all()

    def create_status(self, status_data: dict):
        return self.create(Statuses, status_data)

    def update_status(self, status_id: int, status_data: dict):
        status = self.get_status(status_id)
        if not status:
            return None
        return self.update(status, status_data)

    def delete_status(self, status_id: int):
        status = self.get_status(status_id)
        if not status:
            return None
        return self.delete(status)