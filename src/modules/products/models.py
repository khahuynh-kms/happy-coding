
from typing import Optional
from beanie import Link

from ...core.models.base import TimestampDocument
from ..categories.models import Category


class Product(TimestampDocument):
    name: str
    description: Optional[str]
    price: float
    stock: int = 0
    category: Optional[Link[Category]] = None
    is_active: bool = True

    class Settings:
        name = "products"
        populate_links = True

    class Config:
        from_attributes = True
        populate_by_name = True
