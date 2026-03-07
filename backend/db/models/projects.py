from sqlalchemy import Column, Index, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    client_id = Column(Integer, ForeignKey("clients.id",use_alter=True), nullable=False)

    client = relationship("Clients", back_populates="projects", foreign_keys=[client_id])
    devices = relationship("Devices", back_populates="project", foreign_keys="Devices.project_id")

    runs = relationship("Runs", back_populates="project", foreign_keys="Runs.project_id")

    __table_args__ = (
        Index("project_name_idx", "name"),
    )