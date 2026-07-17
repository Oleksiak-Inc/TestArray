from pydantic import BaseModel, ConfigDict
from .permission import PermissionOut

class GroupPermissionCreate(BaseModel):
    group_id: int
    permission_id: int

class GroupPermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: int
    permission_id: int