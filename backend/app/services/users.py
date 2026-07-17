from db.models.users import Users
from .utils.service import BaseService
from core.security import PasswordHasher

class UserService(BaseService):

    def get_user_by_email(self, email: str):
        user = self.db.query(Users).filter(Users.email == email).first()
        if not user:
            return None
        return user

    def get_user_by_id(self, user_id: int):
        return self.get_by_id(Users, user_id)
    
    def list_users(self):
        return self.db.query(Users).all()
    
    def update_user(self, user_id: int, user_data: dict) -> Users | None:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if "password" in user_data and user_data["password"] is not None:
            user_data["password"] = PasswordHasher.hash(user_data["password"])
        return self.update(user, user_data)

    def delete_user(self, user_id: int) -> Users | None:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        return self.delete(user)

