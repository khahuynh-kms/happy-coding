from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from ..products.schemas import ProductResponse

from ..users.schemas import UserResponse


class OrderItemCreate(BaseModel):
    product_id: PydanticObjectId
    quantity: int


class OrderCreate(BaseModel):
    user_id: PydanticObjectId = None
    items: List[OrderItemCreate]
    status: Optional[str] = "pending"


class OrderItemResponse(BaseModel):
    quantity: int
    subtotal: float
    product: Optional[ProductResponse] = None


class OrderResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    user: UserResponse
    items: List[OrderItemResponse] = None
    total_price: float
    status: str
    ref_order_id: Optional[str] = None
    ref_payment_source: Optional[str] = None
    checkout_url: Optional[str] = None
    payer_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
