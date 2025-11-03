from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: PydanticObjectId
    amount: float
    payment_method: str = "credit_card"
    status: str = "pending"


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None


class PaymentResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    order_id: PydanticObjectId = Field(alias="order._id")
    amount: float
    payment_method: str
    status: str
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
