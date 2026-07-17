from sqlalchemy import Column, Index, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    client = relationship("Clients", back_populates="projects", foreign_keys=[client_id])
    owner = relationship("Users", back_populates="projects", foreign_keys=[owner_id])
    devices = relationship("Devices", back_populates="project", foreign_keys="Devices.project_id")

    runs = relationship("Runs", back_populates="project", foreign_keys="Runs.project_id")

    __table_args__ = (
        Index("project_name_idx", "name"),
    )