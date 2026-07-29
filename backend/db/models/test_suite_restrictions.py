from sqlalchemy import Column, ForeignKey, Index, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class TestSuiteRestrictions(Base):
    __tablename__ = 'test_suite_restrictions'
    
    test_suite_id = Column(Integer, ForeignKey('test_suites.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    
    test_suite = relationship('TestSuites', back_populates='restrictions', foreign_keys=[test_suite_id])
    project = relationship('Projects', back_populates='test_suite_restrictions', foreign_keys=[project_id])
    
    __table_args__ = (
        Index('restriction_test_suite_idx', 'test_suite_id'), 
        Index('restriction_project_idx', 'project_id')
        )