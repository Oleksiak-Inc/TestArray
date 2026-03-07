from sqlalchemy import Column, Index, Integer, String, Text, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Statuses(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True)
    status_set_id = Column(Integer, ForeignKey("status_sets.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)

    status_set = relationship("StatusSets", back_populates="statuses", foreign_keys=[status_set_id])
    executions = relationship("Executions", back_populates="status", foreign_keys="Executions.status_id")

    __table_args__ = (
        Index("status_name_idx", "name"),
        Index("status_status_set_idx", "status_set_id"),
    )