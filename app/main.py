# app/main.py
import os
from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List
from tortoise.exceptions import DoesNotExist, IntegrityError
from pydantic import BaseModel
from models import User

app = FastAPI()

# 用於 PATCH 更新的 Pydantic 模型，所有欄位都是可選的
class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

# 從 Tortoise ORM 模型建立 Pydantic 模型
# UserIn_Pydantic 用於輸入 (建立使用者)，排除唯讀欄位如 id 和 created_at
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
# UserOut_Pydantic 用於輸出 (回傳使用者)，為安全起見排除密碼欄位
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password", ))

# 從環境變數讀取資料庫連線 URL，如果找不到則使用預設值
DB_URL = os.getenv("DB_URL", "postgres://user:password@db:5432/fastapi_db")

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
async def root():
    return {"message": "FastAPI + Tortoise ORM is running!"}

@app.get("/users/", response_model=List[UserOut_Pydantic])
async def get_users():
    return await User.all()

@app.get("/users/{user_id}", response_model=UserOut_Pydantic)
async def get_user(user_id: int):
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@app.patch("/users/{user_id}", response_model=UserOut_Pydantic)
async def update_user(user_id: int, user_update: UserUpdate):
    try:
        db_user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 取得客戶端實際傳送的欄位
    update_data = user_update.dict(exclude_unset=True)

    # 再次提醒：密碼應進行雜湊處理
    if "password" in update_data and update_data["password"]:
        # 在真實應用中，應在此處對 update_data["password"] 進行雜湊
        # 例如: update_data["password"] = pwd_context.hash(update_data["password"])
        pass

    try:
        if update_data:  # 僅在有提供更新資料時才執行
            await db_user.update_from_dict(update_data).save()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username '{update_data.get('username')}' already exists.")

    return db_user

@app.post("/users/", response_model=UserOut_Pydantic)
async def create_user(user: UserIn_Pydantic):
    try:
        # 重要：在真實世界的應用中，你必須在儲存前對密碼進行雜湊處理。
        user_obj = await User.create(**user.dict(exclude_unset=True))
        return user_obj
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username '{user.username}' already exists.")

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    try:
        db_user = await User.get(id=user_id)
        await db_user.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
