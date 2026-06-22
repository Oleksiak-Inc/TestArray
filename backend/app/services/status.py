from db.models.statuses import Statuses
from .utils.service import BaseService


class StatusService(BaseService):
    def get_status(self, status_id: int):
        return self.db.query(Statuses).filter(Statuses.id == status_id).first()

    def list_statuses_by_status_set(self, status_set_id: int):
        return self.db.query(Statuses).filter(
            Statuses.status_set_id == status_set_id
        ).all()

    def list_all_statuses(self):
        return self.db.query(Statuses).all()

    def create_status(self, status_data: dict):
        status = Statuses(**status_data)
        self.db.add(status)
        self.commit_and_refresh(status)
        return status

    def update_status(self, status_id: int, status_data: dict):
        status = self.get_status(status_id)
        if not status:
            return None
        for key, value in status_data.items():
            setattr(status, key, value)
        self.commit_and_refresh(status)
        return status

    def delete_status(self, status_id: int):
        status = self.get_status(status_id)
        if not status:
            return None
        self.db.delete(status)
        self.db.commit()
        return status