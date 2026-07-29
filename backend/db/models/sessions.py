from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship


class Sessions(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)

    user = relationship(
        "Users",
        foreign_keys=[user_id],
        back_populates="sessions",
    )
    revocations = relationship(
        "Revocations",
        foreign_keys="Revocations.target_session_id",
        back_populates="target_session",
    )

    __table_args__ = (
        Index("session_user_id_idx", "user_id"),
        Index("session_token_idx", "token"),
    )