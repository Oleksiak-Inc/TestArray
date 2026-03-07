from sqlalchemy import Column, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class Resolutions(Base):
    __tablename__ = "resolutions"

    id = Column(Integer, primary_key=True)
    h = Column(Integer, nullable=False)
    w = Column(Integer, nullable=False)

    attachments = relationship(
        "Attachments",
        back_populates="resolution",
        foreign_keys="Attachments.resolution_id"
    )

    __table_args__ = (
        UniqueConstraint("h", "w", name="resolutions_hw_unique"),
    )