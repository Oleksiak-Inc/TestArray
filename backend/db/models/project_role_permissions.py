from sqlalchemy import Column, ForeignKey, Index, Integer
from db.base import Base
from sqlalchemy.orm import relationship

class ProjectRolePermissions(Base):
    __tablename__ = 'project_role_permissions'

    role_id = Column(Integer, ForeignKey('project_roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)

    role = relationship('ProjectRoles', back_populates='role_permissions')
    permission = relationship('Permissions', back_populates='project_role_permissions')

    __table_args__ = (
        Index('project_role_permissions_role_idx', 'role_id'),
        Index('project_role_permissions_permission_idx', 'permission_id'),
    )
