from fastapi import APIRouter, HTTPException, Query
from typing import List

from src.core.libs.paypal import paypal_service
from ...core.libs.paypal.paypal_type import (
    PayPalConfirmPaymentSourceRequest, PayPalOrderRequest
)
from ...core.libs.paypal.paypal_builder import PayPalRequestBuilder

from .service import order_service
from ..orders.schemas import OrderCreate, OrderResponse
from ..products.service import product_service
from ..users.service import user_service


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(order_data: OrderCreate):
    total = 0
    order_items = []

    user = await user_service.find_one(order_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User {order_data.user_id} not found")

    for item in order_data.items:
        product_id = item.product_id
        product = await product_service.find_one(product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {product_id} is not found")

        if item.quantity > product.stock:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"The quantity of item {item.product_id}"
                    "is out of stock"
                )
            )

        subtotal = product.price * item.quantity
        total += subtotal

        item = item.model_dump(exclude={"product_id"})
        order_items.append({
            **item,
            "subtotal": subtotal,
            "product": product
        })

    db_order_data = order_data.model_dump(exclude={"user_id"})
    db_order_data["user"] = user
    db_order_data["total_price"] = total
    db_order_data["items"] = order_items

    order = await order_service.create(db_order_data)

    # create payment order to paypal
    order_data = order.model_dump()

    order_payload = PayPalRequestBuilder.build(order_data, PayPalOrderRequest)
    confirm_payment_source_payload = PayPalRequestBuilder.build(
        order_data,
        PayPalConfirmPaymentSourceRequest
    )

    payment_order = await paypal_service.create_order(order_payload)

    await paypal_service.confirm_payment_source(
        order_id=payment_order["id"],
        data=confirm_payment_source_payload
    )

    # update stock for each product
    for item in order.items:
        await product_service.increase(
            item.product.id,
            {"stock": -item.quantity}
        )

    return await order_service.update(
        order.id, {
            "ref_order_id": payment_order["id"],
            "ref_payment_source": "paypal",
            "checkout_url": payment_order["links"][1]["href"],
        }
    )


@router.get("/", response_model=List[OrderResponse])
async def get_all_orders():
    result = await order_service.find_all()
    return result


@router.get("/capture")
async def capture_order(
    ref_order_id: str = Query(..., alias="token"),
    payer_id: str = Query(..., alias="PayerID")
):
    order = await order_service.find_by_ref_order_id(ref_order_id)
    order_id = order.id

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    ref_order_id = order.ref_order_id
    if not ref_order_id:
        raise HTTPException(
            status_code=404,
            detail="Reference order is not found"
        )

    if order.ref_payment_source == "paypal":
        payment = await paypal_service.capture_order(ref_order_id)
        return await order_service.update(
            order_id, {"status": (
                "paid" if payment["status"] == "COMPLETED" else "pending"
            ),
                "payer_id": payer_id
            }
        )

    raise HTTPException(
        status_code=500,
        detail=f"Payment source {order.ref_payment_source} is not supported"
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    return await order_service.find_one(order_id)


@router.get("/{order_id}/provider")
async def get_order_detail_from_provider(order_id: str):
    order = await order_service.find_one(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    ref_order_id = order.ref_order_id
    if not ref_order_id:
        raise HTTPException(
            status_code=404,
            detail="Reference order is not found"
        )

    if order.ref_payment_source == "paypal":
        ref_order = await paypal_service.get_order_detail(ref_order_id)
        return {
            "ref_order": ref_order,
            "order": order.model_dump()
        }
    raise HTTPException(
        status_code=500,
        detail=f"Payment source {order.ref_payment_source} is not supported"
    )


@router.delete("/{order_id}")
async def delete_order(order_id: str):
    success = await order_service.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}
