
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from beanie import Link, PydanticObjectId

from ..categories.schemas import CategoryResponse

from ..categories.models import Category


class ProductBase(BaseModel):
    name: str = Field(..., example="iPhone 16")
    description: Optional[str] = Field(None, example="Latest Apple smartphone")
    price: float = Field(..., example=1299.99)
    stock: int = Field(0, example=50)
    category_id: Optional[PydanticObjectId] = Field(
        None, example="652f95f7f4209b8f22dca333")
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[PydanticObjectId] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: PydanticObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True
