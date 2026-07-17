
from sqlalchemy import Column, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship


class RelationTypes(Base):
    __tablename__ = "relation_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


