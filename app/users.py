# app/api/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError # type: ignore

from models import User
from schemas import UserIn_Pydantic, UserOut_Pydantic, UserUpdate
from security import get_current_user, pwd_context

router = APIRouter()

@router.post("/", response_model=UserOut_Pydantic, status_code=201)
async def create_user(user: UserIn_Pydantic): # type: ignore
    try:
        user_data = user.dict(exclude_unset=True)
        user_data["password"] = pwd_context.hash(user_data["password"])
        user_obj = await User.create(**user_data)
        return user_obj
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username '{user.username}' already exists.")

@router.get("/me", response_model=UserOut_Pydantic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user's information."""
    return current_user

@router.get("/", response_model=List[UserOut_Pydantic])
async def get_users():
    return await User.all()

@router.get("/{user_id}", response_model=UserOut_Pydantic)
async def get_user(user_id: int):
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@router.patch("/{user_id}", response_model=UserOut_Pydantic)
async def update_user(user_id: int, user_update: UserUpdate):
    try:
        db_user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["password"] = pwd_context.hash(update_data["password"])

    try:
        if update_data:
            await db_user.update_from_dict(update_data).save()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username '{update_data.get('username')}' already exists.")

    return db_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    try:
        db_user = await User.get(id=user_id)
        await db_user.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")