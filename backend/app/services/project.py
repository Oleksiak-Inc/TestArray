from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects
from utils.service import BaseService

class ProjectService(BaseService):

    def get_project(self, project_id: int):
        return self.db.query(Projects).filter(Projects.id == project_id).first()
    
    def get_project_with_client(self, project_id: int):
        return self.db.query(Projects).filter(Projects.id == project_id).options(
            joinedload(Projects.client)
        ).first()
    
    def create_project(self, project_data):
        project = Projects(**project_data)
        self.db.add(project)
        self.commit_and_refresh(project)
        return project
    
    def update_project(self, project_id: int, project_data):
        project = self.get_project(project_id)
        for key, value in project_data.items():
            setattr(project, key, value)
        self.commit_and_refresh(project)
        return project
    
    