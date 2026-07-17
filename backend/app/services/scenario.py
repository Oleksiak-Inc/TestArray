from db.models.scenarios import Scenarios
from .utils.service import BaseService


class ScenarioService(BaseService):
    def get_scenario(self, scenario_id: int):
        return self.get_by_id(Scenarios, scenario_id)

    def get_scenario_by_name(self, name: str):
        return self.db.query(Scenarios).filter(Scenarios.name == name).first()

    def list_scenarios(self):
        return self.db.query(Scenarios).all()

    def create_scenario(self, scenario_data):
        return self.create(Scenarios, scenario_data)

    def update_scenario(self, scenario_id: int, scenario_data):
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        return self.update(scenario, scenario_data)

    def delete_scenario(self, scenario_id: int):
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        return self.delete(scenario)
