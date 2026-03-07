from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(..., min_length=8)

class UserUpdateSelf(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)

class UserUpdateAdmin(BaseModel):
    user_group_id: int | None = None
    user_type_id: int | None = None
    active: bool | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    active: bool
    user_type_id: int
    user_group_id: int | None
    created_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True