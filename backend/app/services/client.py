from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects
from .utils.service import BaseService

class ClientService(BaseService):
    def get_client(self, client_id: int):
        return self.get_by_id(Clients, client_id)

    def get_client_with_projects(self, client_id: int):
        return self.db.query(Clients).filter(Clients.id == client_id).options(
            joinedload(Clients.projects)
        ).first()

    def create_client(self, client_data):
        return self.create(Clients, client_data)

    def update_client(self, client_id: int, client_data):
        client = self.get_client(client_id)
        if not client:
            return None
        return self.update(client, client_data)

    def delete_client(self, client_id: int):
        client = self.get_client(client_id)
        if not client:
            return None
        return self.delete(client)