from pydantic import BaseModel, Field

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

    class Config:
        from_attributes = True