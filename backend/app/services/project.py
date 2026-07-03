from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects
from .utils.service import BaseService

class ProjectService(BaseService):

    def get_project(self, project_id: int):
        return self.get_by_id(Projects, project_id)
    
    def get_project_with_client(self, project_id: int):
        return self.db.query(Projects).filter(Projects.id == project_id).options(
            joinedload(Projects.client)
        ).first()
    
    def create_project(self, project_data):
        return self.create(Projects, project_data)
    
    def update_project(self, project_id: int, project_data):
        project = self.get_project(project_id)
        if not project:
            return None
        return self.update(project, project_data)

    def delete_project(self, project_id: int):
        project = self.get_project(project_id)
        if not project:
            return None
        return self.delete(project)
    