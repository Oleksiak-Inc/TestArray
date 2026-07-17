from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship


class ExecutionRelationships(Base):
    __tablename__ = "execution_relationships"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    related_execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    relation_type_id = Column(Integer, ForeignKey("relation_types.id"), nullable=False)

    execution = relationship("Executions", foreign_keys=[execution_id], back_populates="source_relationships")
    related_execution = relationship("Executions", foreign_keys=[related_execution_id], back_populates="target_relationships")
    relation_type = relationship("RelationTypes", foreign_keys=[relation_type_id])

    __table_args__ = (
        UniqueConstraint("execution_id", "related_execution_id", name="unique_execution_rel"),
        Index("execution_relationship_execution_idx", "execution_id"),
        Index("execution_relationship_related_execution_idx", "related_execution_id"),
        Index("execution_relationship_relation_type_idx", "relation_type_id"),
    )
