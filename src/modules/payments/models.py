
from datetime import datetime, timezone
from typing import Literal, Optional

from beanie import Link
from pydantic import Field

from ..orders.models import Order
from ...core.models.base import TimestampDocument


class Payment(TimestampDocument):
    order: Link[Order]
    amount: float
    method: Literal["credit_card", "paypal", "bank_transfer"]
    status: Literal["pending", "completed", "failed"] = "pending"
    paid_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    transaction_id: Optional[str] = None

    class Settings:
        name = "payments"
