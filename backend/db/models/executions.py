from sqlalchemy import Column, Index, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class Executions(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True)

    device_id = Column(Integer, ForeignKey("devices.id",use_alter=True), nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id",use_alter=True), nullable=False)
    test_case_version_id = Column(Integer, ForeignKey("test_case_versions.id",use_alter=True), nullable=False)

    executed_by = Column(Integer, ForeignKey("users.id",use_alter=True), nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id",use_alter=True), nullable=False)

    attachment_id = Column(Integer, ForeignKey("attachments.id",use_alter=True), nullable=True)
    resolution_id = Column(Integer, ForeignKey("resolutions.id",use_alter=True), nullable=True)

    actual_result = Column(Text)
    executed_at = Column(DateTime(timezone=True))

    execution_order = Column(Integer, nullable=False)

    device = relationship("Devices", back_populates="executions", foreign_keys=[device_id])
    run = relationship("Runs", back_populates="executions", foreign_keys=[run_id])
    test_case_version = relationship("TestCaseVersions", back_populates="executions", foreign_keys=[test_case_version_id])
    executor = relationship("Users", foreign_keys=[executed_by], back_populates="executions")
    status = relationship("Statuses", back_populates="executions", foreign_keys=[status_id])
    attachment = relationship("Attachments", back_populates="executions", foreign_keys=[attachment_id])
    resolution = relationship("Resolutions", back_populates="executions", foreign_keys=[resolution_id])

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "test_case_version_id",
            name="execution_run_version_unique"
        ),
        Index("execution_status_idx", "status_id"),
        Index("execution_executor_idx", "executed_by"),
        Index("execution_device_idx", "device_id"),
        Index("execution_attachment_idx", "attachment_id"),
        Index("execution_run_idx", "run_id"),
        Index("execution_test_case_version_idx", "test_case_version_id"),
    )