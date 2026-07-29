from sqlalchemy import Column, Integer, String, Text
from db.base import Base
from sqlalchemy.orm import relationship

class UserTypes(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    # legacy model kept for migration compatibility; no active relationships