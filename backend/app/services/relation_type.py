from db.models.relation_types import RelationTypes
from .utils.service import BaseService

class RelationTypeService(BaseService):
    def list_relation_types(self):
        return self.db.query(RelationTypes).all()

    def get_relation_type(self, type_id: int):
        return self.get_by_id(RelationTypes, type_id)

    def get_relation_type_by_name(self, name: str):
        return self.db.query(RelationTypes).filter(RelationTypes.name == name).first()

    def create_relation_type(self, data: dict):
        return self.create(RelationTypes, data)

    def update_relation_type(self, type_id: int, data: dict):
        rel_type = self.get_relation_type(type_id)
        if not rel_type:
            return None
        return self.update(rel_type, data)

    def delete_relation_type(self, type_id: int):
        rel_type = self.get_relation_type(type_id)
        if not rel_type:
            return None
        return self.delete(rel_type)