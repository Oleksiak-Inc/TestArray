from sqlalchemy import Column, Index, Integer, String, DateTime, Text, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Runs(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    started_at = Column(DateTime(timezone=True))
    done_at = Column(DateTime(timezone=True))

    test_suite_metadata = Column(Text)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("Projects", back_populates="runs", foreign_keys=[project_id])
    executions = relationship("Executions", back_populates="run", foreign_keys="Executions.run_id")

    __table_args__ = (
        Index("run_name_idx", "name"),
        Index("run_project_idx", "project_id"),
    )