from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    img_url: Optional[str] = None

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class UserDetailsSchema(BaseModel):
    email: str 
    username: Optional[str]
    full_name: str
    img_url: Optional[str] = None

    class Config:
        from_attributes = True

    @property
    def username(self):
        return self.username if self.username else self.email


class CeateUserSchema(UserDetailsSchema):
    password: str = Field(..., min_length=8, max_length=50)


class LoginUserSchema(BaseModel):
    email: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8, max_length=50)


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=50)
    new_password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str = Field(..., min_length=8, max_length=50)



class UserResponseSchema(BaseModel):
    message: str
    data: TokenSchema


class RefreshTokenSchema(BaseModel):
    refresh: str
