from db.models.users import Users
from sqlalchemy.orm import Session
from .utils.service import BaseService
from app.api.utils.auth import hash_password

class UserService(BaseService):

    def get_user_by_email(self, email: str):
        user = self.db.query(Users).filter(Users.email == email).first()
        if not user:
            return None
        return user

    def get_user_by_id(self, user_id: int):
        return self.db.query(Users).filter(Users.id == user_id).first()
    
    def list_users(self):
        return self.db.query(Users).all()
    
    def update_user(self, user_id: int, user_data: dict) -> Users | None:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if "password" in user_data and user_data["password"] is not None:
            user_data["password"] = hash_password(user_data["password"])
        for key, value in user_data.items():
            setattr(user, key, value)
        self.commit_and_refresh(user)
        return user

    def delete_user(self, user_id: int) -> Users | None:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        self.db.delete(user)
        self.db.commit()
        return user

