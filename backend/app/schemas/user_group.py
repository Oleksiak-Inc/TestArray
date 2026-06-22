from pydantic import BaseModel, Field, ConfigDict

class UserGroupBase(BaseModel):
    name: str = Field(..., max_length=100)


class UserGroupCreate(UserGroupBase):
    owner_id: int


class UserGroupUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    owner_id: int | None = None


class UserGroupOut(UserGroupBase):
    id: int
    owner_id: int
    created_by_id: int

    model_config = ConfigDict(from_attributes=True)