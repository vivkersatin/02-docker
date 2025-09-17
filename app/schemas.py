"""
定義 API 的資料驗證模型 (schemas)。
使用 Pydantic 來定義請求和回應的資料結構，確保資料的型別和格式正確。
"""

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator # type: ignore
from models import User

# --- Pydantic Models for API ---

# 用於部分更新使用者的模型，所有欄位都是可選的
class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

# 用於 /auth/token 端點的回應模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 用於儲存 JWT token payload 中資料的模型
class TokenData(BaseModel):
    username: str | None = None

# --- Tortoise Pydantic Models ---

# 從 User 模型自動建立用於「輸入」的 Pydantic 模型 (例如，建立使用者時)
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
# 從 User 模型自動建立用於「輸出」的 Pydantic 模型 (例如，獲取使用者資訊時)，並排除敏感的 password 欄位
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password", ))