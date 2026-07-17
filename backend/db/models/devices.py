from sqlalchemy import Column, Index, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Devices(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name_external = Column(String(255))
    name_internal = Column(String(255))
    cpu = Column(String(255))
    gpu = Column(String(255))
    ram = Column(String(255))

    project = relationship("Projects", back_populates="devices", foreign_keys=[project_id])
    executions = relationship("Executions", back_populates="device", foreign_keys="Executions.device_id")

    __table_args__ = (
        Index("device_project_idx", "project_id"),
    )