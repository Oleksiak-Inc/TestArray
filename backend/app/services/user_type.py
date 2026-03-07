from db.models.user_types import UserTypes
from sqlalchemy.orm import Session

class UserTypeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_type_by_id(self, user_type_id: int):
        return self.db.query(UserTypes).filter(UserTypes.id == user_type_id).first()
    
    def get_user_type_by_name(self, name: str):
        return self.db.query(UserTypes).filter(UserTypes.name == name).first()