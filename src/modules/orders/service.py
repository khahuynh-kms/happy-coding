from .models import Order, OrderItem
from ...core.services.base import BaseService


class OrderService(BaseService[Order]):
    def __init__(self):
        super().__init__(Order)

    async def find_by_ref_order_id(self, ref_order_id: str):
        item = await Order.find_one(
            Order.ref_order_id == ref_order_id,
        )
        await self._fetch_nested_links(item)
        return item


class OrderItemService(BaseService[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)


order_item_service = OrderItemService()
order_service = OrderService()
