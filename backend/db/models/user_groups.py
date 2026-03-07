from sqlalchemy import Column, Index, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class UserGroups(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True)

    # use_alter ensures the FK is added after both tables exist, avoiding circular migration issues
    created_by_id = Column(Integer, ForeignKey("users.id", use_alter=True), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", use_alter=True), nullable=False)

    name = Column(String, unique=True)

    # ---- relationships ----
    created_by = relationship(
        "Users",
        foreign_keys=[created_by_id],
        back_populates="groups_created"
    )

    owner = relationship(
        "Users",
        foreign_keys=[owner_id],
        back_populates="groups_owned"
    )

    members = relationship(
        "Users",
        foreign_keys="Users.user_group_id",
        back_populates="user_group"
    )

    __table_args__ = (
        Index("user_group_owner_idx", "owner_id"),
        Index("user_group_created_by_idx", "created_by_id"),
    )