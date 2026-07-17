#join table between user groups and users

from sqlalchemy import Column, ForeignKey, Index, Integer

from db.base import Base

from sqlalchemy.orm import relationship


class GroupsMembers(Base):
    __tablename__ = "groups_members"

    group_id = Column(Integer, ForeignKey("user_groups.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    group = relationship("UserGroups", back_populates="members")
    user = relationship("Users", back_populates="groups_member")

    __table_args__ = (
        Index("group_member_group_idx", "group_id"),
        Index("group_member_user_idx", "user_id"),
    )