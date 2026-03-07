from db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class TestSuites(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    suitcases = relationship(
        "Suitcases", 
        back_populates="test_suite",
        foreign_keys="Suitcases.test_suite_id"
    )