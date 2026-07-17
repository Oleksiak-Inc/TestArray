from sqlalchemy.orm import joinedload
from db.models.executions import Executions
from db.models.projects import Projects
from db.models.runs import Runs
from .utils.service import BaseService

class RunService(BaseService):
    
    def get_run(self, run_id):
        return self.get_by_id(Runs, run_id)
    
    def get_run_with_project(self, run_id):
        return self.db.query(Runs).filter(Runs.id == run_id).options(
            joinedload(Runs.project)
        ).first()
    
    def get_run_with_project_and_client(self, run_id):
        return self.db.query(Runs).filter(Runs.id == run_id).options(
            joinedload(Runs.project).joinedload(Projects.client)
        ).first()

    def list_runs_by_project(self, project_id):
        return self.db.query(Runs).filter(Runs.project_id == project_id).all()
    
    def create_run(self, run_data):
        return self.create(Runs, run_data)
    
    def update_run(self, run_id, run_data):
        run = self.get_run(run_id)
        if not run:
            return None

        if "done_at" in run_data and run_data["done_at"] is not None:
            related_executions = self.db.query(Executions).filter(Executions.run_id == run_id).all()
            if not all(item.status_id is not None for item in related_executions):
                raise ValueError("Cannot mark a run as done before all executions have a status")

        return self.update(run, run_data)

    def delete_run(self, run_id):
        run = self.get_run(run_id)
        if not run:
            return None
        return self.delete(run)