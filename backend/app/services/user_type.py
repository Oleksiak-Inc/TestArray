from db.models.user_types import UserTypes
from .utils.service import BaseService

class UserTypeService(BaseService):
    
    def get_user_type_by_id(self, user_type_id: int):
        return self.get_by_id(UserTypes, user_type_id)
    
    def get_user_type_by_name(self, name: str):
        return self.db.query(UserTypes).filter(UserTypes.name == name).first()

    def list_user_types(self):
        return self.db.query(UserTypes).all()
    
    def create_user_type(self, user_type_data):
        return self.create(UserTypes, user_type_data)
    
    def update_user_type(self, user_type_id, user_type_data):
        user_type = self.get_user_type_by_id(user_type_id)
        if not user_type:
            return None
        return self.update(user_type, user_type_data)

    def delete_user_type(self, user_type_id: int):
        user_type = self.get_user_type_by_id(user_type_id)
        if not user_type:
            return None
        return self.delete(user_type)