from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest

from ....modules.categories.schemas import CategoryResponse
from beanie import PydanticObjectId

category_id = PydanticObjectId()


@pytest.fixture
def mock_category_data():
    return CategoryResponse(
        id=category_id,
        name="Electronics",
        description="Electronic gadgets and devices",
        slug="electronics",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_create_category(
    test_client,
    test_db,
    mock_category_data
):
    mocked_data = mock_category_data

    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.create = AsyncMock(return_value=mocked_data)

        category_data = {
            "name": "Electronics",
            "description": "Electronic gadgets and devices",
            "slug": "electronics"
        }

        response = await test_client.post(
            "/categories/", json=category_data)

        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert data["slug"] == category_data["slug"]
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_categories(
    test_client,
    test_db,
    mock_category_data
):
    mocked_data = [mock_category_data]

    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.find_all = AsyncMock(return_value=mocked_data)

        response = await test_client.get("/categories/")

        data = response.json()
        print(data)
        assert len(data) == 1
        assert data[0]["id"] == str(mocked_data[0].id)
        assert data[0]["name"] == mocked_data[0].name
        assert data[0]["description"] == mocked_data[0].description


@pytest.mark.asyncio
async def test_get_categories_empty(
    test_client,
    test_db
):
    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.find_all = AsyncMock(return_value=[])

        response = await test_client.get("/categories/")

        data = response.json()
        assert response.status_code == 200
        assert data == []


async def test_get_category(
    test_client,
    test_db,
    mock_category_data
):
    mocked_data = mock_category_data

    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.find_one = AsyncMock(return_value=mocked_data)

        response = await test_client.get(f"/categories/{mocked_data.id}")

        data = response.json()
        assert response.status_code == 200
        assert data["name"] == mocked_data.name
        assert data["description"] == mocked_data.description


@pytest.mark.asyncio
async def test_get_category_not_found(
    test_client,
    test_db
):
    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.find_one = AsyncMock(return_value=None)

        response = await test_client.get(
            f"/categories/{PydanticObjectId()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_update_category(
    test_client,
    test_db,
    mock_category_data
):
    mocked_data = mock_category_data

    update_data = {
        "name": "Updated Electronics",
        "description": "Updated description for electronics"
    }

    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.update = AsyncMock(return_value={
            **mocked_data.model_dump(),
            "name": update_data["name"],
            "description": update_data["description"],
        })

        response = await test_client.put(
            f"/categories/{mocked_data.id}", json=update_data)

        data = response.json()
        assert response.status_code == 200
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_update_category_not_found(
    test_client,
    test_db
):
    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.update = AsyncMock(return_value=None)

        update_data = {
            "name": "Updated Electronics",
            "description": "Updated description for electronics"
        }

        response = await test_client.put(
            f"/categories/{PydanticObjectId()}", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_delete_category(
    test_client,
    test_db,
    mock_category_data
):
    mocked_data = mock_category_data

    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.delete = AsyncMock(return_value=True)

        response = await test_client.delete(
            f"/categories/{mocked_data.id}")

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_category_not_found(
    test_client,
    test_db
):
    with (
        patch("src.modules.categories.router.category_service")
        as mock_category_service
    ):
        mock_category_service.delete = AsyncMock(return_value=False)

        response = await test_client.delete(
            f"/categories/{PydanticObjectId()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"
