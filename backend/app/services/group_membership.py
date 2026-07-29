from db.models.groups_members import GroupsMembers
from db.models.users import Users
from db.models.user_groups import UserGroups
from .utils.service import BaseService

class GroupMembershipService(BaseService):
    def add_member(self, group_id: int, user_id: int) -> GroupsMembers:
        group = self.db.query(UserGroups).filter(UserGroups.id == group_id).first()
        
        if not group:
            raise ValueError("Group does not exist")
        
        user = self.db.query(Users).filter(Users.id == user_id).first()

        if not user:
            raise ValueError("User does not exist")

        membership = GroupsMembers(group_id=group_id, user_id=user_id)
        self.add(membership)
        self.commit()
        self.refresh(membership)
        return membership

    def remove_member(self, group_id: int, user_id: int) -> bool:
        membership = self.db.query(GroupsMembers).filter(
            GroupsMembers.group_id == group_id,
            GroupsMembers.user_id == user_id
        ).first()
        if not membership:
            return False
        self.delete(membership)
        return True

    def list_group_members(self, group_id: int) -> list[Users]:
        group = self.db.query(UserGroups).filter(UserGroups.id == group_id).first()
        if not group:
            return []
        # join through members relationship
        return [m.user for m in group.members]

    def list_user_groups(self, user_id: int) -> list[UserGroups]:
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return []
        return [m.group for m in user.groups_member]