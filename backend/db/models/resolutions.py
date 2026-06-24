from sqlalchemy import Column, Integer, UniqueConstraint
from db.base import Base
from sqlalchemy.orm import relationship

class Resolutions(Base):
    __tablename__ = "resolutions"

    id = Column(Integer, primary_key=True)
    h = Column(Integer, nullable=False)
    w = Column(Integer, nullable=False)

    executions = relationship(
        "Executions",
        back_populates="resolution",
        foreign_keys="Executions.resolution_id"
    )

    __table_args__ = (
        UniqueConstraint("h", "w", name="resolutions_hw_unique"),
    )