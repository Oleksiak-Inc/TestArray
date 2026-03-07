from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class Attachments(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)

    parent_attachment_id = Column(Integer, ForeignKey("attachments.id",use_alter=True), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id",use_alter=True), nullable=False)
    resolution_id = Column(Integer, ForeignKey("resolutions.id",use_alter=True), nullable=True)

    filename = Column(String)
    relative_path = Column(String)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    presentmon_version = Column(String)

    settings = Column(JSON)

    parent = relationship(
        "Attachments",
        remote_side=[id],
        backref="children"
    )

    uploader = relationship("Users", back_populates="uploads", foreign_keys=[uploaded_by])
    resolution = relationship("Resolutions", back_populates="attachments", foreign_keys=[resolution_id])
    executions = relationship("Executions", back_populates="attachment", foreign_keys="Executions.attachment_id")


    __table_args__ = (
        Index("attachment_parent_idx", "parent_attachment_id"),
        Index("attachment_uploaded_by_idx", "uploaded_by"),
        Index("attachment_filename_idx", "filename"),
        Index("attachment_uploaded_at_idx", "uploaded_at"),
        Index("attachment_resolution_idx", "resolution_id"),
    )