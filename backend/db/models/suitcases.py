from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class Suitcases(Base):
    __tablename__ = "suitcases"

    id = Column(Integer, primary_key=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    test_suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=False)

    test_case = relationship("TestCases", back_populates="suitcases", foreign_keys=[test_case_id])
    test_suite = relationship("TestSuites", back_populates="suitcases", foreign_keys=[test_suite_id])

    __table_args__ = (
        UniqueConstraint("test_case_id", "test_suite_id"),
        Index("suitcase_test_case_idx", "test_case_id"),
        Index("suitcase_test_suite_idx", "test_suite_id"),
    )