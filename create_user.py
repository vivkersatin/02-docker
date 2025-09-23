import asyncio
from tortoise import Tortoise
from app.api.models import User
from app.api.security import pwd_context
import os

async def create_test_user():
    DB_URL = os.getenv("DB_URL", "postgres://user:password@db:5432/fastapi_db")
    await Tortoise.init(db_url=DB_URL, modules={"models": ["app.api.models"]})
    await Tortoise.generate_schemas()

    username = "testuser"
    password = "testpassword"

    try:
        # 檢查使用者是否已存在
        existing_user = await User.get_or_none(username=username)
        if existing_user:
            print(f"使用者 '{username}' 已存在。")
            return

        hashed_password = pwd_context.hash(password)
        await User.create(username=username, password=hashed_password)
        print(f"使用者 '{username}' 已成功創建。")
    except Exception as e:
        print(f"創建使用者時發生錯誤: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(create_test_user())
