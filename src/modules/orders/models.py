
from typing import List, Optional
from beanie import Link
from pydantic import BaseModel

from ..users.models import User
from ..products.models import Product
from ...core.models.base import TimestampDocument


class OrderItem(BaseModel):
    product: Link[Product]
    quantity: int = 1
    subtotal: float


class Order(TimestampDocument):
    user: Link[User] = None
    items: List[OrderItem]
    total_price: float
    status: str = "pending"  # pending, paid, shipped, delivered, cancelled
    ref_order_id: Optional[str] = None  # reference to payment gateway order id
    ref_payment_source: Optional[str] = None  # e.g., PayPal, Stripe
    checkout_url: Optional[str] = None
    refund_url: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    payer_id: Optional[str] = None

    class Settings:
        name = "orders"

    class Config:
        from_attributes = True
        populate_by_name = True
