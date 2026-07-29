from sqlalchemy import Column, Integer, String, Text
from db.base import Base
from sqlalchemy.orm import relationship
class ProjectRoles(Base):
    __tablename__ = 'project_roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    rank = Column(Integer, nullable=False)

    members = relationship('ProjectMembers', back_populates='role')
    role_permissions = relationship(
        'ProjectRolePermissions',
        back_populates='role',
        cascade='all, delete-orphan',
    )