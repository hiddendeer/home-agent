"""添加 last_hydration_remind_at 字段到 users 表。

使用方式：
    python scripts/add_hydration_field.py
"""

import asyncio
from sqlalchemy import text
from app.infrastructure.database import engine


async def add_field():
    """添加字段到数据库。"""
    async with engine.begin() as conn:
        try:
            # 检查字段是否已存在
            result = await conn.execute(
                text("SHOW COLUMNS FROM users LIKE 'last_hydration_remind_at'")
            )
            if result.fetchone():
                print("字段 last_hydration_remind_at 已存在，无需添加")
                return

            # 添加字段
            await conn.execute(
                text("""
                    ALTER TABLE users
                    ADD COLUMN last_hydration_remind_at DATETIME NULL
                    COMMENT '上次喝水提醒时间'
                    AFTER is_superuser
                """)
            )
            print("✅ 成功添加 last_hydration_remind_at 字段")
        except Exception as e:
            print(f"❌ 错误: {e}")
            raise


if __name__ == "__main__":
    print("正在添加 last_hydration_remind_at 字段...")
    asyncio.run(add_field())
