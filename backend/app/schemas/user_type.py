from pydantic import BaseModel, Field, ConfigDict

class UserTypeBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class UserTypeCreate(UserTypeBase):
    pass


class UserTypeUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None


class UserTypeOut(UserTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)