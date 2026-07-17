from db.models.permissions import Permissions
from .utils.service import BaseService

class PermissionService(BaseService):
    def list_permissions(self):
        return self.db.query(Permissions).all()

    def get_permission(self, permission_id: int):
        return self.get_by_id(Permissions, permission_id)

    def get_permission_by_code(self, code: str):
        return self.db.query(Permissions).filter(Permissions.code == code).first()

    def create_permission(self, data: dict):
        return self.create(Permissions, data)

    def delete_permission(self, permission_id: int):
        perm = self.get_permission(permission_id)
        if not perm:
            return None
        return self.delete(perm)