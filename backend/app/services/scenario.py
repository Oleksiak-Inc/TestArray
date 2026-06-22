from db.models.scenarios import Scenarios
from sqlalchemy.orm import Session
from .utils.service import BaseService


class ScenarioService(BaseService):
    def get_scenario(self, scenario_id: int):
        return self.db.query(Scenarios).filter(Scenarios.id == scenario_id).first()

    def get_scenario_by_name(self, name: str):
        return self.db.query(Scenarios).filter(Scenarios.name == name).first()

    def list_scenarios(self):
        return self.db.query(Scenarios).all()

    def create_scenario(self, scenario_data):
        scenario = Scenarios(**scenario_data)
        self.db.add(scenario)
        self.commit_and_refresh(scenario)
        return scenario

    def update_scenario(self, scenario_id: int, scenario_data):
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        for key, value in scenario_data.items():
            setattr(scenario, key, value)
        self.commit_and_refresh(scenario)
        return scenario

    def delete_scenario(self, scenario_id: int):
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        self.db.delete(scenario)
        self.db.commit()
        return scenario
