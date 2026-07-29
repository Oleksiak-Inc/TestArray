from sqlalchemy import Column, Index, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # use_alter ensures the FK is added after both tables exist, avoiding circular migration issues
    #user_group_id = Column(Integer, ForeignKey("user_groups.id", use_alter=True), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)

    active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

    groups_member = relationship(
        "GroupsMembers",
        back_populates="user"
    )

    projects_member = relationship(
        "ProjectMembers",
        back_populates="user"
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
    
    edits = relationship(
        "Attachments",
        foreign_keys="Attachments.edited_by",
        back_populates="editor"
    )
    
    executions = relationship(
        "Executions", 
        foreign_keys="Executions.executed_by", 
        back_populates="executor")
    updated_executions = relationship(
        "Executions",
        foreign_keys="Executions.updated_by",
        back_populates="updater"
    )
    assigned_executions = relationship(
        "Executions",
        foreign_keys="Executions.assigned_to",
        back_populates="assignee"
    )

    created_test_case_versions = relationship(
        "TestCaseVersions", 
        foreign_keys="TestCaseVersions.created_by", 
        back_populates="creator")
    
    sessions = relationship(
        "Sessions",
        foreign_keys="Sessions.user_id", 
        back_populates="user")

    triggered_incidents = relationship(
        "Incidents",
        foreign_keys="Incidents.triggered_by_user_id",
        back_populates="triggered_by_user",
    )

    targeted_incidents = relationship(
        "Incidents",
        foreign_keys="Incidents.target_user_id",
        back_populates="target_user",
    )

    revocations = relationship(
        "Revocations",
        foreign_keys="Revocations.revoked_by_user_id",
        back_populates="revoked_by_user",
    )
    
    projects = relationship(
        "Projects",
        foreign_keys="Projects.owner_id",
        back_populates="owner"
    )

    __table_args__ = (
        #Index("user_user_group_idx", "user_group_id"),
    )