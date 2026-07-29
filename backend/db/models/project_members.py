from sqlalchemy import Column, ForeignKey, Index, Integer
from db.base import Base
from sqlalchemy.orm import relationship
class ProjectMembers(Base):
    __tablename__ = 'project_members'
    
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('project_roles.id'), nullable=False)
    
    project = relationship('Projects', back_populates='members')
    user = relationship('Users', back_populates='projects_member')
    role = relationship('ProjectRoles', back_populates='members')
    
    __table_args__ = (
        Index('project_member_project_idx', 'project_id'), 
        Index('project_member_user_idx', 'user_id'), 
        Index('project_member_role_idx', 'role_id')
        )