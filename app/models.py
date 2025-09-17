"""
定義應用程式的資料庫模型。
使用 Tortoise ORM 來描述資料庫中的資料表結構。
"""

from tortoise import fields # type: ignore
from tortoise.models import Model # type: ignore

class User(Model):
    """
    使用者模型，對應資料庫中的 'user' 資料表。
    """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, description="使用者名稱")
    password = fields.CharField(max_length=128, description="雜湊後的密碼")
    created_at = fields.DatetimeField(auto_now_add=True, description="建立時間")
