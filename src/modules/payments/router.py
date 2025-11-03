
from fastapi import APIRouter, HTTPException
from typing import List
from .service import payment_service
from .schemas import PaymentCreate, PaymentResponse, PaymentUpdate

from ..orders.service import order_service
router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(payment_data: PaymentCreate):
    try:
        order = await order_service.find_one(payment_data.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        payment_data["order"] = order
        payment = await payment_service.create(payment_data)
        return PaymentResponse(
            id=str(payment.id),
            order_id=str(payment.order.id),
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PaymentResponse])
async def list_payments():
    payments = await payment_service.find_all()
    return [
        PaymentResponse(
            id=payment.id,
            order_id=payment.order._id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
        for payment in payments
    ]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    payment = await payment_service.find_one(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentResponse(
        id=payment.id,
        order_id=payment.order._id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(payment_id: str, data: PaymentUpdate):
    payment = await payment_service.update(payment_id, data)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentResponse(
        id=str(payment.id),
        order_id=str(payment.order.id),
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


@router.delete("/{payment_id}")
async def delete_payment(payment_id: str):
    success = await payment_service.delete(payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}
