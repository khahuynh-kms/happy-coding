import pytest

from datetime import datetime
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId
from ....modules.products.schemas import ProductResponse

from ....modules.users.schemas import UserResponse
from ....modules.orders.schemas import OrderItemResponse, OrderResponse


order_id = PydanticObjectId()
user_id = PydanticObjectId()
product_id = PydanticObjectId()
category_id = PydanticObjectId()


@pytest.fixture
def order_data():
    return OrderResponse(
        id=order_id,
        user=UserResponse(
            id=user_id,
            email="user@example.com",
            full_name="John Doe",
            is_active=True,
            role="user",
        ),
        items=[
            OrderItemResponse(
                quantity=2,
                subtotal=19.99,
                product=ProductResponse(
                    id=product_id,
                    name="Sample Product",
                    description="A sample product description",
                    price=9.99,
                    stock=100,
                    slug="sample-product",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    category_id=category_id,
                )
            )
        ],
        total_price=39.98,
        status="pending",
        ref_order_id="ORDER12345",
        ref_payment_source="paypal",
        checkout_url="https://example.com/checkout",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_create_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.user_service")
      as mock_user_service,
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
      patch("src.modules.orders.router.product_service")
      as mock_product_service,  
      patch("src.modules.orders.router.paypal_service")
      as mock_paypal_service
    ):
        mock_user_service.find_one = AsyncMock(return_value=mocked_data.user)
        mock_product_service.find_one = AsyncMock(
          return_value=mocked_data.items[0].product
        )
        mock_product_service.increase = AsyncMock(return_value=None)
        mock_order_service.create = AsyncMock(return_value=mocked_data)
        mock_order_service.update = AsyncMock(return_value=mocked_data)
        
        mock_paypal_service.create_order = AsyncMock(return_value={
            "id": "PAYPAL_ORDER_123",
            "links": [
                {"href": "https://example.com/cancel", "rel": "cancel"},
                {"href": "https://example.com/approve", "rel": "approve"},
            ]
        })
        mock_paypal_service.confirm_payment_source = AsyncMock(
          return_value=None
        )
        mock_paypal_service.get_order_detail = AsyncMock(
          return_value={"status": "COMPLETED"}
        )
        
        order_payload = {
            "user_id": str(user_id),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": 2
                }
            ]
        }

        response = await test_client.post(
            "/orders/", json=order_payload)

        data = response.json()
        print("data:", data)
        assert data["user"]["id"] == str(user_id)
        assert data["total_price"] == mocked_data.total_price
        assert len(data["items"]) == len(mocked_data.items)
        assert data["status"] == mocked_data.status
        assert data["ref_order_id"] == mocked_data.ref_order_id
        assert data["ref_payment_source"] == mocked_data.ref_payment_source
        assert data["checkout_url"] == mocked_data.checkout_url
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_not_found_user_of_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.user_service")
      as mock_user_service,
      patch("src.modules.orders.router.product_service")
      as mock_product_service,  
    ):
        mock_user_service.find_one = AsyncMock(return_value=None)
        mock_product_service.find_one = AsyncMock(
          return_value=mocked_data.items[0].product
        )
        
        order_payload = {
            "user_id": str(user_id),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": 2
                }
            ]
        }

        response = await test_client.post(
            "/orders/", json=order_payload)

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == f"User {order_payload['user_id']} not found"


@pytest.mark.asyncio
async def test_create_not_found_product_of_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.user_service")
      as mock_user_service,
      patch("src.modules.orders.router.product_service")
      as mock_product_service,  
    ):
        mock_user_service.find_one = AsyncMock(return_value=mocked_data.user)
        mock_product_service.find_one = AsyncMock(
          return_value=None
        )
        
        order_payload = {
            "user_id": str(user_id),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": 2
                }
            ]
        }

        response = await test_client.post(
            "/orders/", json=order_payload)

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == f"Product with id {product_id} is not found"


@pytest.mark.asyncio
async def test_create_out_of_stock_product_of_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.user_service")
      as mock_user_service,
      patch("src.modules.orders.router.product_service")
      as mock_product_service,  
    ):
        mock_user_service.find_one = AsyncMock(return_value=mocked_data.user)
        out_of_stock_product = mocked_data.items[0].product
        out_of_stock_product.stock = 1  # less than order quantity
        mock_product_service.find_one = AsyncMock(
          return_value=out_of_stock_product
        )
        
        order_payload = {
            "user_id": str(user_id),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": 2
                }
            ]
        }

        response = await test_client.post(
            "/orders/", json=order_payload)

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == (
            f"The quantity of item {product_id}is out of stock"
        )


@pytest.mark.asyncio
async def test_get_all_orders(
    test_client,
    test_db,
    order_data
):
    mocked_data = [order_data]

    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
    ):
        mock_order_service.find_all = AsyncMock(return_value=mocked_data)

        response = await test_client.get("/orders/")

        data = response.json()
        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["id"] == str(mocked_data[0].id)
        assert data[0]["user"]["id"] == str(mocked_data[0].user.id)
        assert data[0]["total_price"] == mocked_data[0].total_price
        assert data[0]["status"] == mocked_data[0].status
        assert data[0]["ref_order_id"] == mocked_data[0].ref_order_id
        assert (
          data[0]["ref_payment_source"] == mocked_data[0].ref_payment_source
        )
        assert data[0]["checkout_url"] == mocked_data[0].checkout_url


@pytest.mark.asyncio
async def test_get_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
    ):
        mock_order_service.find_one = AsyncMock(return_value=mocked_data)

        response = await test_client.get(f"/orders/{mocked_data.id}")

        data = response.json()
        print("data:", data)
        assert data["user"]["id"] == str(user_id)
        assert data["total_price"] == mocked_data.total_price
        assert len(data["items"]) == len(mocked_data.items)
        assert data["status"] == mocked_data.status
        assert data["ref_order_id"] == mocked_data.ref_order_id
        assert data["ref_payment_source"] == mocked_data.ref_payment_source
        assert data["checkout_url"] == mocked_data.checkout_url
        assert response.status_code == 200
        

@pytest.mark.asyncio
async def test_get_order_not_found(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
    ):
        mock_order_service.find_one = AsyncMock(return_value=None)

        response = await test_client.get(f"/orders/{str(mocked_data.id)}")

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_capture_order(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data

    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
      patch("src.modules.orders.router.paypal_service")
      as mock_paypal_service
    ):
        mock_order_service.find_by_ref_order_id = AsyncMock(
          return_value=mocked_data
        )
        mock_order_service.update = AsyncMock(return_value=mocked_data)
        mock_paypal_service.get_order_detail = AsyncMock(
          return_value={"status": "COMPLETED"}
        )
        mock_paypal_service.capture_order = AsyncMock(
          return_value={"status": "COMPLETED"}
        )

        response = await test_client.get(
            "/orders/capture?token=ORDER12345&PayerID=PAYER123"
        )

        data = response.json()
        assert data["user"]["id"] == str(user_id)
        assert data["total_price"] == mocked_data.total_price
        assert len(data["items"]) == len(mocked_data.items)
        assert data["status"] == mocked_data.status
        assert data["ref_order_id"] == mocked_data.ref_order_id
        assert data["ref_payment_source"] == mocked_data.ref_payment_source
        assert data["checkout_url"] == mocked_data.checkout_url
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_capture_order_not_found(
    test_client,
    test_db,
    order_data
):  
    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
      patch("src.modules.orders.router.paypal_service")
      as mock_paypal_service
    ):
        mock_order_service.find_by_ref_order_id = AsyncMock(
          return_value=None
        )
        mock_order_service.update = AsyncMock(return_value=None)
        mock_paypal_service.capture_order = AsyncMock(
          return_value={"status": "COMPLETED"}
        )

        response = await test_client.get(
            "/orders/capture?token=ORDER12345&PayerID=PAYER123"
        )

        data = response.json()
        assert response.status_code == 404
        assert data["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_capture_order_not_paypal_source(
    test_client,
    test_db,
    order_data
):
    mocked_data = order_data
    
    with (
      patch("src.modules.orders.router.order_service")
      as mock_order_service,
    ):
        mocked_data.ref_payment_source = "not_paypal"
        mock_order_service.find_by_ref_order_id = AsyncMock(
          return_value=mocked_data
        )
        mock_order_service.update = AsyncMock(return_value=mocked_data)

        response = await test_client.get(
            "/orders/capture?token=ORDER12345&PayerID=PAYER123"
        )

        data = response.json()
        assert data["detail"] == "Payment source not_paypal is not supported"
        assert response.status_code == 500
