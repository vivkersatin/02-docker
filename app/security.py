"""
處理所有與安全相關的功能。
包含密碼雜湊、JWT token 的建立與驗證，以及使用者身份的依賴注入。
"""

import os
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from tortoise.exceptions import DoesNotExist # type: ignore

from models import User
from schemas import TokenData

# --- Security & JWT Settings ---
# 警告: 在真實世界的應用中，絕不應硬編碼 SECRET_KEY。應從環境變數或安全的配置管理系統中讀取。
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
# 設定密碼雜湊上下文，使用 bcrypt 演算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Scheme ---
# 定義 OAuth2 密碼流程的 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Helper Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼是否與雜湊後的密碼相符。"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """建立一個 JWT access token。"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """解碼 JWT token，並從資料庫中獲取當前使用者。這是一個依賴項，可用於保護 API 端點。"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 從 token 的 payload 中獲取使用者名稱 (subject)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        # 根據使用者名稱從資料庫中查找使用者實例
        return await User.get(username=username)
    except (JWTError, DoesNotExist):
        # 如果 token 無效、過期，或在資料庫中找不到該使用者，則拋出異常
        raise credentials_exception