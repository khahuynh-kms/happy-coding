import httpx

from ...config.config import app_settings


paypal_config = app_settings.payment.paypal

URI = paypal_config.uri
EMAIL = paypal_config.email
PASSWORD = paypal_config.password
REGION = paypal_config.region
CLIENT_ID = paypal_config.client_id
PAYPAL_CLIENT_SECRET = paypal_config.client_secret
API_URI = paypal_config.api_uri

routes = {
    "login": "/v1/oauth2/token",
    "payments.list": "/v2/payments/payment",
    "payments.create": "/v2/payments/payment",
    "orders.create": "/v2/checkout/orders",
    "orders.capture": (
        lambda order_id: f"/v2/checkout/orders/{order_id}/capture"
    ),
    "orders.detail": (
        lambda order_id: f"/v2/checkout/orders/{order_id}"
    ),
    "orders.confirm_payment_source": (
        lambda order_id:
            f"/v2/checkout/orders/{order_id}/confirm-payment-source"
    ),

}

# Paypal cycle
# 1. Create an order => return ref order id and save it to db
# 2. Confirm the order => by finding ref order id of order
# 3. By get url from step 2 or get ref order detail => receive payment url
# 4. Return it to FE side for payer pay
# (in this step we can set up a webhook to auto capture)
# 5. After it, we need to capture the payment


async def register_paypal_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URI}{routes['login']}",
            auth=(CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def create_order(data):
    token = await register_paypal_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URI}{routes['orders.create']}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json=data
        )
        response.raise_for_status()
        return response.json()


async def create_payment(data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URI}{routes['payments.create']}",
            headers={
                "Authorization": f"Bearer {await register_paypal_token()}"
            },
            json=data
        )
        return response.json()


async def confirm_payment_source(order_id, data):
    token = await register_paypal_token()
    print(token)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URI}{routes['orders.confirm_payment_source'](order_id)}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json=data
        )
        print(response.json())

        return response.json()


async def get_order_detail(order_id):
    token = await register_paypal_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URI}{routes['orders.detail'](order_id)}",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )
        response.raise_for_status()
        return response.json()


async def capture_order(order_id):
    token = await register_paypal_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URI}{routes['orders.capture'](order_id)}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={}
        )
        return response.json()


async def list_payments(limit: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URI}{routes['payments.list']}",
            headers={
                "Authorization": f"Bearer {await register_paypal_token()}"
            },
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
