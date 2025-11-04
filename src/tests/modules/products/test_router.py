from datetime import datetime
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId
import pytest

from ....modules.categories.schemas import CategoryResponse
from ....modules.products.schemas import ProductResponse

product_id = PydanticObjectId()
category_id = PydanticObjectId()
updated_product_id = PydanticObjectId()


@pytest.fixture
def mock_product_data():
    """Provides a mock ProductResponse object."""
    return ProductResponse(
        id=product_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        name="Sample Product",
        description="A product for testing",
        price=49.99,
        stock=100,
        is_active=True,
        category_id=category_id,
        category=CategoryResponse(
            id=category_id,
            name="Sample Category",
            slug="sample-category",
            description="A category for testing",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    )


@pytest.mark.asyncio
async def test_create_product(
    test_client,
    test_db,
    mock_product_data
):
    mocked_data = mock_product_data

    with (
        patch("src.modules.products.router.category_service")
        as mock_category_service,
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):

        mock_category_service.find_one = AsyncMock(
            return_value=mock_product_data.category)
        mock_product_service.create = AsyncMock(return_value=mocked_data)

        product_data = {
            "name": "Sample Product",
            "description": "A product for testing",
            "price": 49.99,
            "stock": 100,
            "is_active": True,
            "category_id": str(mocked_data.category_id)
        }

        response = await test_client.post("/products/", json=product_data)

        data = response.json()
        assert response.status_code == 200
        assert data["name"] == mocked_data.name
        assert data["description"] == mocked_data.description
        assert data["price"] == mocked_data.price
        assert data["stock"] == mocked_data.stock
        assert data["is_active"] == mocked_data.is_active
        assert data["category_id"] == str(mocked_data.category_id)


@pytest.mark.asyncio
async def test_create_product_category_not_found(
    test_client,
    test_db,
    mock_product_data
):
    with (
        patch("src.modules.products.router.category_service")
        as mock_category_service,
    ):
        mock_category_service.find_one = AsyncMock(return_value=None)

        product_data = {
            "name": "Sample Product",
            "description": "A product for testing",
            "price": 49.99,
            "stock": 100,
            "is_active": True,
            "category_id": str(mock_product_data.category_id)
        }

        response = await test_client.post("/products/", json=product_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_get_products(
    test_client,
    test_db,
    mock_product_data
):
    mocked_data = [mock_product_data]

    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.find_all = AsyncMock(return_value=mocked_data)

        response = await test_client.get("/products/")

        data = response.json()
        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["name"] == mocked_data[0].name
        assert data[0]["description"] == mocked_data[0].description
        assert data[0]["price"] == mocked_data[0].price
        assert data[0]["stock"] == mocked_data[0].stock
        assert data[0]["is_active"] == mocked_data[0].is_active
        assert data[0]["category_id"] == str(mocked_data[0].category_id)


@pytest.mark.asyncio
async def test_get_products_empty(
    test_client,
    test_db
):
    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.find_all = AsyncMock(return_value=[])

        response = await test_client.get("/products/")

        data = response.json()
        assert response.status_code == 200
        assert data == []


async def test_get_product(
    test_client,
    test_db,
    mock_product_data
):
    mocked_data = mock_product_data

    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.find_one = AsyncMock(return_value=mocked_data)

        response = await test_client.get(f"/products/{mocked_data.id}")

        data = response.json()
        assert response.status_code == 200
        assert data["name"] == mocked_data.name
        assert data["description"] == mocked_data.description
        assert data["price"] == mocked_data.price
        assert data["stock"] == mocked_data.stock
        assert data["is_active"] == mocked_data.is_active
        assert data["category_id"] == str(mocked_data.category_id)


@pytest.mark.asyncio
async def test_get_product_not_found(
    test_client,
    test_db
):
    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.find_one = AsyncMock(return_value=None)

        response = await test_client.get(f"/products/{product_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_update_product(
    test_client,
    test_db,
    mock_product_data
):
    mocked_data = mock_product_data

    with (
        patch("src.modules.products.router.category_service")
        as mock_category_service,
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        update_data = {
            "name": "Updated Product",
            "description": "An updated product for testing",
        }

        mock_category_service.find_one = AsyncMock(
            return_value=mock_product_data.category)

        response_data = mocked_data
        response_data.name = update_data["name"]
        response_data.description = update_data["description"]
        mock_product_service.update = AsyncMock(return_value=response_data)

        response = await test_client.put(
            f"/products/{mocked_data.id}", json=update_data)

        data = response.json()
        print(data)
        assert response.status_code == 200
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_update_product_not_found(
    test_client,
    test_db,
    mock_product_data
):
    with (
        patch("src.modules.products.router.category_service")
        as mock_category_service,
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_category_service.find_one = AsyncMock(
            return_value=mock_product_data.category)
        mock_product_service.update = AsyncMock(return_value=None)

        update_data = {
            "name": "Updated Product",
            "description": "An updated product for testing",
        }

        response = await test_client.put(
            f"/products/{mock_product_data.id}", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_update_product_category_not_found(
    test_client,
    test_db,
    mock_product_data
):
    with (
        patch("src.modules.products.router.category_service")
        as mock_category_service,
    ):
        mock_category_service.find_one = AsyncMock(return_value=None)
        update_data = {
            "category_id": str(PydanticObjectId())
        }
        response = await test_client.put(
            f"/products/{mock_product_data.id}", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_delete_product(
    test_client,
    test_db
):
    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.delete = AsyncMock(return_value=True)

        response = await test_client.delete(f"/products/{product_id}")

        data = response.json()
        assert response.status_code == 200
        assert data["success"] is True
        assert data["message"] == "Product deleted"


@pytest.mark.asyncio
async def test_delete_product_not_found(
    test_client,
    test_db
):
    with (
        patch("src.modules.products.router.product_service")
        as mock_product_service
    ):
        mock_product_service.delete = AsyncMock(return_value=False)

        response = await test_client.delete(f"/products/{product_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
