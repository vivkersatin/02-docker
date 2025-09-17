# app/main.py
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise # type: ignore
from tortoise.contrib.pydantic import pydantic_model_creator # type: ignore
from typing import List
from tortoise.exceptions import DoesNotExist, IntegrityError # type: ignore
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import User

# --- 安全性與 JWT 設定 ---
# 重要：在真實世界的應用中，絕對不要將 SECRET_KEY 硬編碼在程式碼中。
# 應該從環境變數讀取，以確保安全。
# 你可以使用 `openssl rand -hex 32` 來產生一個安全的金鑰。
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- 密碼雜湊設定 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 設定 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Pydantic 模型 ---
class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password", ))

# --- 輔助函式 ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證純文字密碼與雜湊後的密碼是否相符"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """建立 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """解碼 JWT 並取得目前使用者"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    try:
        user = await User.get(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except DoesNotExist:
        raise credentials_exception

# --- FastAPI 應用程式實例 ---
app = FastAPI()

# --- 資料庫設定 ---
# 從環境變數讀取資料庫連線 URL，如果找不到則使用預設值
DB_URL = os.getenv("DB_URL", "postgres://user:password@db:5432/fastapi_db")

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# --- API 端點 ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await User.get(username=form_data.username)
    except DoesNotExist:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    # This is the root endpoint
    return {"message": "FastAPI + Tortoise ORM is running!"}

@app.get("/users/me", response_model=UserOut_Pydantic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """取得目前登入使用者的資訊"""
    return current_user

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

    # 如果提供了新密碼，則進行雜湊處理
    if "password" in update_data and update_data["password"]:
        hashed_password = pwd_context.hash(update_data["password"])
        update_data["password"] = hashed_password

    try:
        if update_data:  # 僅在有提供更新資料時才執行
            await db_user.update_from_dict(update_data).save()
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Username '{update_data.get('username')}' already exists.")

    return db_user

@app.post("/users/", response_model=UserOut_Pydantic)
async def create_user(user: UserIn_Pydantic): # type: ignore
    try:
        user_data = user.dict(exclude_unset=True)
        # 對密碼進行雜湊
        hashed_password = pwd_context.hash(user_data["password"])
        user_data["password"] = hashed_password
        
        user_obj = await User.create(**user_data)
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
