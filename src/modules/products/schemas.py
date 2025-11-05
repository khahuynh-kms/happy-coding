
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
    is_active: bool = True

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "iPhone 16",
                    "description": "Latest Apple smartphone",
                    "price": 1299.99,
                    "stock": 50,
                }
            ]
        }
    )


class ProductCreate(ProductBase):
    category_id: Optional[PydanticObjectId]
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "iPhone 16",
                    "description": "Latest Apple smartphone",
                    "price": 1299.99,
                    "stock": 50,
                    "category_id": "64b8f0f2e1b1c8a1d2e3f4g5",
                }
            ]
        }
    )


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
