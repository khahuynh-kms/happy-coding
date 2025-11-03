
from typing import Optional

from ...core.models.base import TimestampDocument


class Category(TimestampDocument):
    name: str
    slug: str
    description: Optional[str] = None

    class Settings:
        name = "categories"
