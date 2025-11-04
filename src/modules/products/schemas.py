
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from beanie import PydanticObjectId

from ..categories.schemas import CategoryResponse


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: Optional[PydanticObjectId]
    is_active: bool = True

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "iPhone 16",
                    "description": "Latest Apple smartphone",
                    "price": 1299.99,
                    "stock": 50,
                    "category_id": "507f1f77bcf86cd799439011",
                }
            ]
        }
    )


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

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
