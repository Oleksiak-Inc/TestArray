from sqlalchemy import Column, Index, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship

class StatusSets(Base):
    __tablename__ = "status_sets"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    statuses = relationship(
        "Statuses",
        back_populates="status_set",
        foreign_keys="Statuses.status_set_id"
    )
    
    test_cases = relationship(
        "TestCases",
        back_populates="status_set",
        foreign_keys="TestCases.status_set_id"
    )
