# app/schemas.py
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User

# --- Pydantic Models for API ---

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# --- Tortoise Pydantic Models ---

UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password", ))