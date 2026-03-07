from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects

class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def get_client(self, client_id):
        return self.db.query(Clients).filter(Clients.id == client_id).first()

    def get_client_with_projects(self, client_id):
        return self.db.query(Clients).filter(Clients.id == client_id).options(
            joinedload(Clients.projects)
        ).first()

    def create_client(self, client_data):
        client = Clients(**client_data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update_client(self, client_id, client_data):
        client = self.get_client(client_id)
        for key, value in client_data.items():
            setattr(client, key, value)
        self.db.commit()
        self.db.refresh(client)
        return client