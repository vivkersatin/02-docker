# app/main.py
import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise # type: ignore

from api import auth, users

# --- FastAPI 應用程式實例 ---
app = FastAPI(title="My FastAPI Project")

# --- 資料庫設定 ---
DB_URL = os.getenv("DB_URL", "postgres://user:password@db:5432/fastapi_db")

# --- 掛載 Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

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
    """Root endpoint providing a welcome message."""
    return {"message": "FastAPI + Tortoise ORM is running!"}
