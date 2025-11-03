
from typing import List
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from ...core.auth.security_service import SecurityService

from .schemas import UserCreate, UserResponse, UserUpdate
from .service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    existing = await user_service.find_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    create_user_data = user_data.model_copy(update={
        "password": SecurityService.hash_password(user_data.password)
    }).model_dump(exclude_none=True)
    return await user_service.create(create_user_data)


@router.get("/", response_model=List[UserResponse])
async def list_users():
    return await user_service.find_all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: PydanticObjectId):
    user = await user_service.find_one(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: PydanticObjectId, update_data: UserUpdate):
    user = await user_service.find_one(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    user = await user_service.update(user_id, update_dict)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: PydanticObjectId):
    deleted = await user_service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User deleted"}
