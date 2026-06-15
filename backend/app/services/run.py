from sqlalchemy.orm import Session, joinedload
from db.models.clients import Clients
from db.models.projects import Projects
from db.models.runs import Runs
from .utils.service import BaseService

class RunService(BaseService):
    
    def get_run(self, run_id):
        return self.db.query(Runs).filter(Runs.id == run_id).first()
    
    def get_run_with_project(self, run_id):
        return self.db.query(Runs).filter(Runs.id == run_id).options(
            joinedload(Runs.project)
        ).first()
    
    def get_run_with_project_and_client(self, run_id):
        return self.db.query(Runs).filter(Runs.id == run_id).options(
            joinedload(Runs.project).joinedload(Projects.client)
        ).first()
    
    def create_run(self, run_data):
        run = Runs(**run_data)
        self.db.add(run)
        self.commit_and_refresh(run)
        return run
    
    def update_run(self, run_id, run_data):
        run = self.get_run(run_id)
        if not run:
            return None
        for key, value in run_data.items():
            setattr(run, key, value)
        self.commit_and_refresh(run)
        return run