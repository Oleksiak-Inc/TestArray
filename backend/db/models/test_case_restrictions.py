from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class TestCaseRestrictions(Base):
    __tablename__ = 'test_case_restrictions'
    
    test_case_id = Column(Integer, ForeignKey('test_cases.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    
    test_case = relationship('TestCases', back_populates='restrictions', foreign_keys=[test_case_id])
    project = relationship('Projects', back_populates='test_case_restrictions', foreign_keys=[project_id])
    
    __table_args__ = (
        Index('restriction_test_case_idx', 'test_case_id'), 
        Index('restriction_test_case_project_idx', 'project_id')
        )