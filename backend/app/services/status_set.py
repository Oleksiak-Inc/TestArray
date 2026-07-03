from db.models.status_sets import StatusSets
from sqlalchemy.orm import Session
from .utils.service import BaseService


class StatusSetService(BaseService):
    def get_status_set(self, status_set_id: int):
        return self.get_by_id(StatusSets, status_set_id)

    def get_status_set_by_name(self, name: str):
        return self.db.query(StatusSets).filter(StatusSets.name == name).first()

    def list_status_sets(self):
        return self.db.query(StatusSets).all()

    def create_status_set(self, status_set_data):
        return self.create(StatusSets, status_set_data)

    def update_status_set(self, status_set_id: int, status_set_data):
        status_set = self.get_status_set(status_set_id)
        if not status_set:
            return None
        return self.update(status_set, status_set_data)

    def delete_status_set(self, status_set_id: int):
        status_set = self.get_status_set(status_set_id)
        if not status_set:
            return None
        return self.delete(status_set)
