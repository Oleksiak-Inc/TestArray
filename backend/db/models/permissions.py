from sqlalchemy import Column, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship

class Permissions(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)

    # relationships
    group_permissions = relationship(
        "GroupPermissions",
        back_populates="permission",
        cascade="all, delete-orphan",
    )