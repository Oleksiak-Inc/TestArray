from sqlalchemy.orm import joinedload
from db.models.projects import Projects
from db.models.users import Users
from .utils.service import BaseService

class ProjectService(BaseService):

    def get_project(self, project_id: int):
        return self.get_by_id(Projects, project_id)
    
    def get_project_with_client(self, project_id: int):
        return self.db.query(Projects).filter(Projects.id == project_id).options(
            joinedload(Projects.client)
        ).first()
    
    def create_project(self, project_data):
        if "owner_id" not in project_data or project_data["owner_id"] is None:
            owner = self.db.query(Users).order_by(Users.id.asc()).first()
            if owner is None:
                owner = Users(
                    first_name="System",
                    last_name="Owner",
                    email="system-owner@example.com",
                    password="placeholder",
                    user_type_id=1,
                )
                self.db.add(owner)
                self.db.flush()
            project_data = dict(project_data)
            project_data["owner_id"] = owner.id
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
    