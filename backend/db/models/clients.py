from sqlalchemy import Column, Index, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship

class Clients(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False) 

    projects = relationship(
        "Projects",
        back_populates="client",
        foreign_keys="Projects.client_id"
    )