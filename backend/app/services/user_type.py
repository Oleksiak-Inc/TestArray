from db.models.user_types import UserTypes
from sqlalchemy.orm import Session
from utils.service import BaseService

class UserTypeService(BaseService):
    
    def get_user_type_by_id(self, user_type_id: int):
        return self.db.query(UserTypes).filter(UserTypes.id == user_type_id).first()
    
    def get_user_type_by_name(self, name: str):
        return self.db.query(UserTypes).filter(UserTypes.name == name).first()
    
    def create_user_type(self, user_type_data):
        user_type = UserTypes(**user_type_data)
        self.db.add(user_type)
        self.commit_and_refresh(user_type)
        return user_type
    
    def update_user_type(self, user_type_id, user_type_data):
        user_type = self.get_user_type_by_id(user_type_id)
        if not user_type:
            return None
        for key, value in user_type_data.items():
            setattr(user_type, key, value)
        self.commit_and_refresh(user_type)
        return user_type