"""
處理使用者認證的 API 路由。
主要包含登入以獲取 JWT token 的端點。
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist # type: ignore

from models import User
from schemas import Token
from security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_password

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    處理使用者登入請求，驗證成功後回傳 JWT access token。
    使用 OAuth2PasswordRequestForm 來接收 "username" 和 "password" 表單資料。
    """
    try:
        # 根據使用者名稱從資料庫中查找使用者
        user = await User.get(username=form_data.username)
    except DoesNotExist:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 驗證傳入的密碼是否與資料庫中儲存的雜湊密碼相符
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # 建立 JWT access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}