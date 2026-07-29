from pydantic import BaseModel, ConfigDict, Field

class GroupPermissionCreate(BaseModel):
    group_id: int
    permission_id: int


class GroupMultiplePermissionsCreate(BaseModel):
    group_id: int
    permission_ids: list[int] = Field(..., min_length=1)


class GroupPermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: int
    permission_id: int
