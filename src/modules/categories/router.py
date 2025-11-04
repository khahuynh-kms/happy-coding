
from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from .schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from .service import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse)
async def create_category(data: CategoryCreate):
    return await category_service.create(data)


@router.get("/", response_model=List[CategoryResponse])
async def get_categories():
    return await category_service.find_all()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: PydanticObjectId):
    category = await category_service.find_one(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: PydanticObjectId, data: CategoryUpdate):
    category = await category_service.update(category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: PydanticObjectId):
    success = await category_service.delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
