from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from db.base import Base


class Revocations(Base):
    __tablename__ = "revocations"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    target_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    revoked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incidents", foreign_keys=[incident_id], back_populates="revocations")
    target_session = relationship("Sessions", foreign_keys=[target_session_id], back_populates="revocations")
    revoked_by_user = relationship("Users", foreign_keys=[revoked_by_user_id], back_populates="revocations")
