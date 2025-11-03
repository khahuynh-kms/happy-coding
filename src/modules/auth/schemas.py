from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from ..users.schemas import UserResponse


class AuthBase(BaseModel):
    email: Optional[EmailStr] = None


class LoginWithCredential(AuthBase):
    password: str


class RegisterWithCredential(AuthBase):
    password: str


class ResetPasswordRequest(AuthBase):
    pass


class ResetPassword(BaseModel):
    password: str
    token: str


class UserChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    exp: datetime


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
