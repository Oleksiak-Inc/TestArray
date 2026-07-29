from sqlalchemy import Column, ForeignKey, Index, Integer
from db.base import Base
from sqlalchemy.orm import relationship

class GroupPermissions(Base):
    __tablename__ = "group_permissions"

    group_id = Column(Integer, ForeignKey("user_groups.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

    group = relationship("UserGroups", back_populates="group_permissions")
    permission = relationship("Permissions", back_populates="group_permissions")

    __table_args__ = (
        Index("group_permissions_group_idx", "group_id"),
        Index("group_permissions_permission_idx", "permission_id"),
    )