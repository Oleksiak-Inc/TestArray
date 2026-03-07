from sqlalchemy import Column, Index, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class TestCaseVersions(Base):
    __tablename__ = "test_case_versions"

    id = Column(Integer, primary_key=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    release_ready = Column(Boolean, default=False)
    version = Column(Integer, nullable=False)
    name = Column(String)
    description = Column(Text)
    steps = Column(Text)
    expected_result = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_case = relationship("TestCases", back_populates="versions", foreign_keys=[test_case_id])
    creator = relationship("Users", foreign_keys=[created_by], back_populates="created_test_case_versions")
    executions = relationship("Executions", back_populates="test_case_version", foreign_keys="Executions.test_case_version_id")

    __table_args__ = (
        UniqueConstraint("test_case_id", "version", name="test_case_version_unique"),
        Index("test_case_version_test_case_idx", "test_case_id"),
        Index("test_case_version_created_at_idx", "created_at"),
        Index("test_case_version_created_by_idx", "created_by"),
    )