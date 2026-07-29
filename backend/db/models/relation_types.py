# relation_types.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base

class RelationTypes(Base):
    __tablename__ = "relation_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    execution_relationships = relationship(
        "ExecutionRelationships",
        back_populates="relation_type",
        foreign_keys="ExecutionRelationships.relation_type_id",
    )