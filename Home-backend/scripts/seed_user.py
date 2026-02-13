import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.infrastructure.config import get_settings
from app.models.user import User

async def seed_user():
    settings = get_settings()
    engine = create_async_engine(settings.mysql_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # 检查是否已存在
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.id == 101))
        if result.scalars().first():
            print("用户 ID 101 已存在，跳过初始化。")
            return

        user = User(
            id=101,
            username="mr_chen",
            email="chen@example.com",
            full_name="陈先生",
            hashed_password="fake_password_hash",
            is_active=True
        )
        session.add(user)
        await session.commit()
        print("成功初始化用户：陈先生 (ID: 101)")

if __name__ == "__main__":
    asyncio.run(seed_user())
