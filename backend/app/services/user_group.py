from db.models.user_groups import UserGroups
from .utils.service import BaseService


class UserGroupService(BaseService):
    def get_user_group(self, group_id: int):
        return self.db.query(UserGroups).filter(UserGroups.id == group_id).first()

    def get_user_group_by_name(self, name: str):
        return self.db.query(UserGroups).filter(UserGroups.name == name).first()

    def list_user_groups(self):
        return self.db.query(UserGroups).all()

    def create_user_group(self, group_data: dict):
        group = UserGroups(**group_data)
        self.db.add(group)
        self.commit_and_refresh(group)
        return group

    def update_user_group(self, group_id: int, group_data: dict):
        group = self.get_user_group(group_id)
        if not group:
            return None
        for key, value in group_data.items():
            setattr(group, key, value)
        self.commit_and_refresh(group)
        return group

    def delete_user_group(self, group_id: int):
        group = self.get_user_group(group_id)
        if not group:
            return None
        self.db.delete(group)
        self.db.commit()
        return group