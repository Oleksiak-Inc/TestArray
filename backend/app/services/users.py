from db.models.users import Users
from sqlalchemy.orm import Session
from utils.service import BaseService

class UserService(BaseService):

    def get_user_by_email(self, email: str):
        user = self.db.query(Users).filter(Users.email == email).first()
        if not user:
            return None
        return user

    def get_user_by_id(self, user_id: int):
        return self.db.query(Users).filter(Users.id == user_id).first()