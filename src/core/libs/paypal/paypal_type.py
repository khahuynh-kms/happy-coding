from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .paypal_builder import PayPalRequestInterface
from ...config.config import app_settings


class Money(BaseModel):
    currency_code: str = "USD"
    value: str


class PayPalItem(BaseModel):
    name: str
    quantity: str
    unit_amount: Money
    description: Optional[str] = None
    sku: Optional[str] = None
    category: str = "PHYSICAL_GOODS"


class AmountBreakdown(BaseModel):
    item_total: Money


class AmountWithBreakdown(BaseModel):
    currency_code: str = "USD"
    value: str
    breakdown: AmountBreakdown


class PurchaseUnit(BaseModel):
    reference_id: str
    amount: AmountWithBreakdown
    items: List[PayPalItem]


class ApplicationContext(BaseModel):
    brand_name: str = "My Online Store"
    user_action: str = "PAY_NOW"
    return_url: str
    cancel_url: str
    shipping_preference: str = "NO_SHIPPING"


class PayPalName(BaseModel):
    given_name: str
    surname: str


class PayPalExperienceContext(BaseModel):
    payment_method_preference: str = "IMMEDIATE_PAYMENT_REQUIRED"
    brand_name: str = "My Online Store"
    locale: str = "en-US"
    landing_page: str = "LOGIN"
    shipping_preference: str = "SET_PROVIDED_ADDRESS"
    user_action: str = "PAY_NOW"
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None


class PayPalSource(BaseModel):
    name: PayPalName
    email_address: str
    experience_context: PayPalExperienceContext


class PaymentSource(BaseModel):
    paypal: PayPalSource


@dataclass
class PayPalOrderRequest(BaseModel, PayPalRequestInterface):
    intent: str = "CAPTURE"
    purchase_units: List[PurchaseUnit]
    application_context: ApplicationContext

    @classmethod
    def from_raw(cls, raw_data: Dict[str, Any]) -> "PayPalOrderRequest":
        """
        Converts an application's internal order dictionary
        into a PayPalOrderRequest object.
        """

        # paypal_config = app_settings.payment.paypal
        order_id = str(raw_data["id"])
        total_price = raw_data["total_price"]

        # Map internal order items to PayPal items
        paypal_items = []
        item_total_value = 0.0
        for item in raw_data["items"]:
            product = item["product"]
            item_price = float(product["price"])
            quantity = int(item["quantity"])

            paypal_items.append(
                PayPalItem(
                    name=product["name"],
                    quantity=str(quantity),
                    unit_amount=Money(value=f"{item_price:.2f}"),
                    sku=str(product["id"]),
                )
            )
            item_total_value += item_price * quantity

        # Define the purchase unit for PayPal
        purchase_unit = PurchaseUnit(
            reference_id=order_id,
            items=paypal_items,
            amount=AmountWithBreakdown(
                value=f"{total_price:.2f}",
                breakdown=AmountBreakdown(
                    item_total=Money(value=f"{item_total_value:.2f}")
                ),
            ),
        )

        # Define the application context with return/cancel URLs
        application_context = ApplicationContext(
            return_url="", cancel_url=""
        )

        result = {
            "intent": "CAPTURE",
            "purchase_units": [purchase_unit],
            "application_context": application_context,
        }

        return cls.model_validate(result).model_dump()


@dataclass
class PayPalConfirmPaymentSourceRequest(BaseModel, PayPalRequestInterface):
    payment_source: PaymentSource

    @classmethod
    def from_raw(
        cls, raw_data: Dict[str, Any]
    ) -> "PayPalConfirmPaymentSourceRequest":
        """
        Convert raw input into a PayPalConfirmPaymentSourceRequest
        """

        paypal_settings = app_settings.payment.paypal

        # Expected keys: name, email_address, and experience_context fields
        full_name = raw_data["user"]["full_name"] or ""
        name_parts = full_name.split()

        given_name = name_parts[0] if name_parts else ""
        surname = name_parts[-1] if len(name_parts) > 1 else ""
        paypal_name = {
            "given_name": given_name,
            "surname": surname
        }

        experience_context = {
            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
            "user_action": "PAY_NOW",
            "return_url": f"{app_settings.base_uri}/orders/capture",
        }

        paypal_data = {
            "name": paypal_name,
            "email_address": (
                paypal_settings.mode == 'sandbox'
                and paypal_settings.personal_sandbox_email
                or raw_data["user"]["email"]
            ),
            "experience_context": experience_context,
        }

        result = {"payment_source": {"paypal": paypal_data}}
        return cls.model_validate(result).model_dump()
