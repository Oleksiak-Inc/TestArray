from db.models.group_permissions import GroupPermissions
from db.models.permissions import Permissions
from db.models.user_groups import UserGroups
from .utils.service import BaseService

class GroupPermissionService(BaseService):
    def assign_permission(self, group_id: int, permission_id: int) -> GroupPermissions:
        # check existence
        group = self.db.query(UserGroups).filter(UserGroups.id == group_id).first()
        if not group:
            raise ValueError("Group does not exist")
        perm = self.db.query(Permissions).filter(Permissions.id == permission_id).first()
        if not perm:
            raise ValueError("Permission does not exist")
        # avoid duplicates
        existing = self.db.query(GroupPermissions).filter(
            GroupPermissions.group_id == group_id,
            GroupPermissions.permission_id == permission_id,
        ).first()
        if existing:
            raise ValueError("Permission already assigned to group")
        gp = GroupPermissions(group_id=group_id, permission_id=permission_id)
        return self.save(gp)

    def assign_multiple_permissions(
        self, group_id: int, permission_ids: list[int]
    ) -> list[GroupPermissions]:
        """Assign all requested permissions to a group in one transaction."""
        group = self.db.query(UserGroups).filter(UserGroups.id == group_id).first()
        if not group:
            raise ValueError("Group does not exist")

        if len(permission_ids) != len(set(permission_ids)):
            raise ValueError("Permission IDs must be unique")

        permissions = (
            self.db.query(Permissions)
            .filter(Permissions.id.in_(permission_ids))
            .all()
        )
        found_permission_ids = {permission.id for permission in permissions}
        if len(found_permission_ids) != len(permission_ids):
            raise ValueError("Permission does not exist")

        assigned_permission_ids = {
            permission_id
            for (permission_id,) in self.db.query(GroupPermissions.permission_id)
            .filter(
                GroupPermissions.group_id == group_id,
                GroupPermissions.permission_id.in_(permission_ids),
            )
            .all()
        }
        if assigned_permission_ids:
            raise ValueError("Permission already assigned to group")

        assignments = [
            GroupPermissions(group_id=group_id, permission_id=permission_id)
            for permission_id in permission_ids
        ]
        self.db.add_all(assignments)
        self.db.commit()
        return assignments

    def remove_permission(self, group_id: int, permission_id: int) -> bool:
        gp = self.db.query(GroupPermissions).filter(
            GroupPermissions.group_id == group_id,
            GroupPermissions.permission_id == permission_id,
        ).first()
        if not gp:
            return False
        self.delete(gp)
        return True

    def list_permissions_for_group(self, group_id: int) -> list[Permissions]:
        group = self.db.query(UserGroups).filter(UserGroups.id == group_id).first()
        if not group:
            return []
        return [gp.permission for gp in group.group_permissions]

    def list_groups_for_permission(self, permission_id: int) -> list[UserGroups]:
        perm = self.db.query(Permissions).filter(Permissions.id == permission_id).first()
        if not perm:
            return []
        return [gp.group for gp in perm.group_permissions]
