from db.models.user_groups import UserGroups
from .utils.service import BaseService
from db.models.users import Users


class UserGroupService(BaseService):
    def get_user_group(self, group_id: int):
        return self.get_by_id(UserGroups, group_id)

    def get_user_group_by_name(self, name: str):
        return self.db.query(UserGroups).filter(UserGroups.name == name).first()

    def list_user_groups(self):
        return self.db.query(UserGroups).all()

    def create_user_group(self, group_data: dict):
        owner = self.db.query(Users).filter(Users.id == group_data["owner_id"]).first()
        if not owner:
            raise ValueError("Owner user not found")
        return self.create(UserGroups, group_data)

    def update_user_group(self, group_id: int, group_data: dict):
        group = self.get_user_group(group_id)
        if not group:
            return None
        return self.update(group, group_data)

    def delete_user_group(self, group_id: int):
        group = self.get_user_group(group_id)
        if not group:
            return None
        return self.delete(group)