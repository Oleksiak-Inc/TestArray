from sqlalchemy import Column, Index, Integer, Text, DateTime, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Executions(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    test_case_version_id = Column(Integer, ForeignKey("test_case_versions.id"), nullable=False)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)

    attachment_id = Column(Integer, ForeignKey("attachments.id"), nullable=True)
    resolution_id = Column(Integer, ForeignKey("resolutions.id"), nullable=True)

    actual_result = Column(Text)
    started_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    execution_order = Column(Integer, nullable=False)

    device = relationship("Devices", back_populates="executions", foreign_keys=[device_id])
    run = relationship("Runs", back_populates="executions", foreign_keys=[run_id])
    test_case_version = relationship("TestCaseVersions", back_populates="executions", foreign_keys=[test_case_version_id])
    assignee = relationship("Users", foreign_keys=[assigned_to], back_populates="assigned_executions")
    executor = relationship("Users", foreign_keys=[executed_by], back_populates="executions")
    updater = relationship("Users", foreign_keys=[updated_by], back_populates="updated_executions")
    status = relationship("Statuses", back_populates="executions", foreign_keys=[status_id])
    attachment = relationship("Attachments", back_populates="executions", foreign_keys=[attachment_id])
    resolution = relationship("Resolutions", back_populates="executions", foreign_keys=[resolution_id])
    source_relationships = relationship("ExecutionRelationships", foreign_keys="ExecutionRelationships.execution_id", back_populates="execution")
    target_relationships = relationship("ExecutionRelationships", foreign_keys="ExecutionRelationships.related_execution_id", back_populates="related_execution")

    __table_args__ = (
        Index("execution_status_idx", "status_id"),
        Index("execution_assignee_idx", "assigned_to"),
        Index("execution_executor_idx", "executed_by"),
        Index("execution_updater_idx", "updated_by"),
        Index("execution_device_idx", "device_id"),
        Index("execution_attachment_idx", "attachment_id"),
        Index("execution_run_idx", "run_id"),
        Index("execution_test_case_version_idx", "test_case_version_id"),
    )