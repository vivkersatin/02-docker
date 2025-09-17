"""
應用程式主入口點。
負責初始化 FastAPI 應用、設定 CORS、連接資料庫、掛載 API 路由。
"""
import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise # type: ignore
from fastapi.middleware.cors import CORSMiddleware

# 導入 API 路由模組
import auth, users

app = FastAPI(title="My FastAPI Project")

# --- CORS Middleware ---
# 允許來自我們新前端服務的跨來源請求
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 設定 CORS 中介軟體，允許跨來源請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 資料庫設定 ---
# 從環境變數讀取資料庫 URL，如果未設定則使用預設值
DB_URL = os.getenv("DB_URL", "postgres://user:password@db:5432/fastapi_db")

# --- 掛載 Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# --- Tortoise ORM 初始化 ---
register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# --- 根目錄端點 ---
@app.get("/")
async def root():
    """根目錄端點，提供一個歡迎訊息，可用於健康檢查。"""
    return {"message": "FastAPI + Tortoise ORM is running!"}
