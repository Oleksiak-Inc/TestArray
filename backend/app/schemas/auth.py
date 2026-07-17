from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

class UserLogout(BaseModel):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseSchema):
    sub: int
    exp: int
