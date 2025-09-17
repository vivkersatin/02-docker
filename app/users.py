"""
處理使用者相關操作的 API 路由。
包含使用者的增、刪、改、查 (CRUD) 功能。
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError # type: ignore

from models import User
from schemas import UserIn_Pydantic, UserOut_Pydantic, UserUpdate
from security import get_current_user, pwd_context

router = APIRouter()

@router.post("/", response_model=UserOut_Pydantic, status_code=201)
async def create_user(user: UserIn_Pydantic): # type: ignore
    """建立新使用者，並將密碼進行雜湊處理。"""
    try:
        user_data = user.dict(exclude_unset=True)
        # 使用 pwd_context 對密碼進行雜湊
        user_data["password"] = pwd_context.hash(user_data["password"])
        user_obj = await User.create(**user_data)
        return user_obj
    except IntegrityError:
        # 如果使用者名稱已存在，會觸發資料庫的唯一性約束錯誤
        raise HTTPException(status_code=400, detail=f"Username '{user.username}' already exists.")

@router.get("/me", response_model=UserOut_Pydantic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """獲取當前登入者的個人資訊。這是一個受保護的端點。"""
    return current_user

@router.get("/", response_model=List[UserOut_Pydantic])
async def get_users():
    """獲取所有使用者的列表。"""
    return await User.all()

@router.get("/{user_id}", response_model=UserOut_Pydantic)
async def get_user(user_id: int):
    """根據 ID 獲取單一使用者的資訊。"""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@router.patch("/{user_id}", response_model=UserOut_Pydantic)
async def update_user(user_id: int, user_update: UserUpdate):
    """
    根據 ID 更新使用者的資訊（部分更新）。
    如果提供了新密碼，會對其進行雜湊處理。
    """
    try:
        db_user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 將 Pydantic 模型轉換為字典，並排除未設定的欄位
    update_data = user_update.dict(exclude_unset=True)

    # 如果請求中包含密碼，則進行雜湊處理
    if "password" in update_data and update_data["password"]:
        update_data["password"] = pwd_context.hash(update_data["password"])

    try:
        # 如果有需要更新的資料，則更新並儲存
        if update_data:
            await db_user.update_from_dict(update_data).save()
    except IntegrityError:
        # 處理更新時可能發生的使用者名稱重複問題
        raise HTTPException(status_code=400, detail=f"Username '{update_data.get('username')}' already exists.")

    return db_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """根據 ID 刪除使用者。"""
    try:
        db_user = await User.get(id=user_id)
        await db_user.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")