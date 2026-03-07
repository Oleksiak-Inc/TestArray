from sqlalchemy import Column, Index, Integer, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class TestCases(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    status_set_id = Column(Integer, ForeignKey("status_sets.id"), nullable=False)
    scenario = relationship("Scenarios", back_populates="test_cases", foreign_keys=[scenario_id])
    status_set = relationship("StatusSets", back_populates="test_cases", foreign_keys=[status_set_id])
    versions = relationship("TestCaseVersions", back_populates="test_case", foreign_keys="TestCaseVersions.test_case_id")
    suitcases = relationship("Suitcases", back_populates="test_case", foreign_keys="Suitcases.test_case_id")

    __table_args__ = (
        Index("test_case_scenario_idx", "scenario_id"),
        Index("test_case_status_set_idx", "status_set_id"),
    )