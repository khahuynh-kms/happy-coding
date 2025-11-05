from fastapi import APIRouter, HTTPException
from beanie import Link, PydanticObjectId

from .schemas import ProductCreate, ProductResponse, ProductUpdate


from ..categories.service import category_service
from .service import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(data: ProductCreate):
    if data.category_id:
        category = await category_service.find_one(data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    data = data.model_dump(exclude={"category_id"})
    return await product_service.create({**data, "category": category})


@router.get("/", response_model=list[ProductResponse])
async def get_products():
    return await product_service.find_all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: PydanticObjectId):
    product = await product_service.find_one(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: PydanticObjectId, data: ProductUpdate):
    category = None
    if data.category_id:
        category = await category_service.find_one(data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    data = data.model_dump(exclude={"category_id"}, exclude_unset=True)
    payload = {**data, "category": Link(category)} if category else {**data}
    product = await product_service.update(
        product_id, payload)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
async def delete_product(product_id: PydanticObjectId):
    deleted = await product_service.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Product deleted"}
