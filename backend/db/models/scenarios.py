from sqlalchemy import Column, Index, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship

class Scenarios(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    test_cases = relationship("TestCases", back_populates="scenario", foreign_keys="TestCases.scenario_id")

    