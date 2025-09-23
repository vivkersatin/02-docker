from typing import Optional
from pydantic import BaseModel

# --- User Schemas ---
class UserIn_Pydantic(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserOut_Pydantic(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool

    class Config:
        from_attributes = True # Replaced orm_mode for Pydantic v2

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# --- Book Schemas ---
class BookIn_Pydantic(BaseModel):
    title: str
    author: str
    published_year: int

class BookOut_Pydantic(BaseModel):
    id: int
    title: str
    author: str
    published_year: int

    class Config:
        from_attributes = True # Replaced orm_mode for Pydantic v2