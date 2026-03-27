from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects
from utils.service import BaseService

class ClientService(BaseService):
    def get_client(self, client_id: int):
        return self.db.query(Clients).filter(Clients.id == client_id).first()

    def get_client_with_projects(self, client_id: int):
        return self.db.query(Clients).filter(Clients.id == client_id).options(
            joinedload(Clients.projects)
        ).first()

    def create_client(self, client_data):
        client = Clients(**client_data)
        self.db.add(client)
        self.commit_and_refresh(client)
        return client

    def update_client(self, client_id: int, client_data):
        client = self.get_client(client_id)
        if not client:
            return None
        for key, value in client_data.items():
            setattr(client, key, value)
        self.commit_and_refresh(client)
        return client