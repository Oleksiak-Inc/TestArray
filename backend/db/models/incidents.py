from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from db.base import Base


class Incidents(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category = Column(String(30), nullable=False)
    severity = Column(Enum("low", "medium", "high", "critical", name="incident_severity"), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    triggered_by_user = relationship(
        "Users",
        foreign_keys=[triggered_by_user_id],
        back_populates="triggered_incidents",
    )
    target_user = relationship(
        "Users",
        foreign_keys=[target_user_id],
        back_populates="targeted_incidents",
    )
    revocations = relationship(
        "Revocations",
        foreign_keys="Revocations.incident_id",
        back_populates="incident",
    )
