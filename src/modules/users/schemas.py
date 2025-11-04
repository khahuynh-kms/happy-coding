from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    email_verified: Optional[bool] = None


class UserChangePassword(BaseModel):
    password: str


class UserResponse(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    role: Optional[str]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        from_attributes=True
    )
