

from pydantic import EmailStr
from typing import Optional
from beanie import Indexed
from ...core.models.base import TimestampDocument


class User(TimestampDocument):
    email: EmailStr = Indexed(unique=True)
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    role: Optional[str] = None
    email_verified: bool = False

    class Settings:
        name = "users"
