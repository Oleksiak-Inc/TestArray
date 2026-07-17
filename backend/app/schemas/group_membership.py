from pydantic import BaseModel, ConfigDict

class GroupMembershipCreate(BaseModel):
    group_id: int
    user_id: int

class GroupMembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: int
    user_id: int