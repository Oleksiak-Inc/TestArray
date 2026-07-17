from db.models.execution_relationships import ExecutionRelationships
from .utils.service import BaseService

class ExecutionRelationshipService(BaseService):
    def create_relationship(self, execution_id: int, related_execution_id: int,
                            relation_type_id: int) -> ExecutionRelationships:
        rel = ExecutionRelationships(
            execution_id=execution_id,
            related_execution_id=related_execution_id,
            relation_type_id=relation_type_id
        )
        return self.save(rel)

    def delete_relationship(self, relationship_id: int) -> bool:
        rel = self.get_by_id(ExecutionRelationships, relationship_id)
        if not rel:
            return False
        self.delete(rel)
        return True

    def get_relationships_for_execution(self, execution_id: int):
        return self.db.query(ExecutionRelationships).filter(
            (ExecutionRelationships.execution_id == execution_id) |
            (ExecutionRelationships.related_execution_id == execution_id)
        ).all()