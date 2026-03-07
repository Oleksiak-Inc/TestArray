from sqlalchemy import Column, Index, Integer, String, Text
from db.base import Base
from sqlalchemy.orm import relationship

class UserTypes(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    # ---- relationships ----
    users = relationship(
        "Users",
        foreign_keys="Users.user_type_id",
        back_populates="user_type"
    )