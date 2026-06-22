from db.models.status_sets import StatusSets
from sqlalchemy.orm import Session
from .utils.service import BaseService


class StatusSetService(BaseService):
    def get_status_set(self, status_set_id: int):
        return self.db.query(StatusSets).filter(StatusSets.id == status_set_id).first()

    def get_status_set_by_name(self, name: str):
        return self.db.query(StatusSets).filter(StatusSets.name == name).first()

    def list_status_sets(self):
        return self.db.query(StatusSets).all()

    def create_status_set(self, status_set_data):
        status_set = StatusSets(**status_set_data)
        self.db.add(status_set)
        self.commit_and_refresh(status_set)
        return status_set

    def update_status_set(self, status_set_id: int, status_set_data):
        status_set = self.get_status_set(status_set_id)
        if not status_set:
            return None
        for key, value in status_set_data.items():
            setattr(status_set, key, value)
        self.commit_and_refresh(status_set)
        return status_set

    def delete_status_set(self, status_set_id: int):
        status_set = self.get_status_set(status_set_id)
        if not status_set:
            return None
        self.db.delete(status_set)
        self.db.commit()
        return status_set
