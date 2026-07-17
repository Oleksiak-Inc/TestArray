from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)


class UserUpdateSelf(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)


class UserUpdateAdmin(BaseModel):
    user_type_id: int | None = None
    active: bool | None = None


class UserOut(BaseSchema):
    id: int
    email: str
    first_name: str
    last_name: str
    active: bool
    user_type_id: int
    created_at: datetime
    last_login_at: datetime | None