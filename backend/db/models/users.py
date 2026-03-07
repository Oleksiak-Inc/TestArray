from sqlalchemy import Column, Index, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # use_alter ensures the FK is added after both tables exist, avoiding circular migration issues
    user_group_id = Column(Integer, ForeignKey("user_groups.id", use_alter=True), nullable=True)
    user_type_id = Column(Integer, ForeignKey("user_types.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # ---- relationships ----
    user_type = relationship(
        "UserTypes", 
        foreign_keys=[user_type_id], 
        back_populates="users")

    user_group = relationship(
        "UserGroups",
        foreign_keys=[user_group_id],
        back_populates="members"
    )

    groups_created = relationship(
        "UserGroups",
        foreign_keys="UserGroups.created_by_id",
        back_populates="created_by"
    )

    groups_owned = relationship(
        "UserGroups",
        foreign_keys="UserGroups.owner_id",
        back_populates="owner"
    )

    uploads = relationship(
        "Attachments", 
        foreign_keys="Attachments.uploaded_by", 
        back_populates="uploader")
    
    executions = relationship(
        "Executions", 
        foreign_keys="Executions.executed_by", 
        back_populates="executor")
    
    created_test_case_versions = relationship(
        "TestCaseVersions", 
        foreign_keys="TestCaseVersions.created_by", 
        back_populates="creator")
    
    sessions = relationship(
        "Sessions",
        foreign_keys="Sessions.user_id", 
        back_populates="user")
    
    __table_args__ = (
        Index("user_user_type_idx", "user_type_id"),
        Index("user_user_group_idx", "user_group_id"),
    )