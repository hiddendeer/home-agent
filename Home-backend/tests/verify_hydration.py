import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)

# Ensure app can be imported
sys.path.append(os.getcwd())

import app.database as db
from app.database import Base
from app.models.action import UserActionLog
from app.models.notification import Notification
from app.models.user import User
import app.tasks.hydration
from app.tasks.hydration import _check_logic

# Mock LLM Service
class MockLLMService:
    def __init__(self, settings=None):
        pass
    async def generate(self, prompt, **kwargs):
        print(f"[MOCK LLM] Prompt received: {prompt[:100]}...") # Print more to see context
        if "10 minutes" in prompt:
             return "YES. 您已经超过10分钟没有喝水了，根据规则，请立即补水。"
        return "YES. 需要提醒。"

# Apply Monkeypatch
app.tasks.hydration.LLMService = MockLLMService
print("Monkeypatched LLMService for testing.")

async def create_tables():
    """Create tables if they don't exist."""
    print("Creating tables...")
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

async def setup_data():
    """Setup test data."""
    async with db.async_session_maker() as session:
        # 1. Try to find User 101 first (since we used it before)
        result = await session.execute(select(User).where(User.id == 101))
        user = result.scalars().first()
        
        # 2. If not found, try to find by email
        if not user:
            result = await session.execute(select(User).where(User.email == "front@example.com"))
            user = result.scalars().first()
            
        # 3. If still not found, create it
        if not user:
            print("User not found. Creating test user...")
            user = User(username="frontend_user", email="front@example.com", hashed_password="xxx", full_name="Frontend User")
            session.add(user)
            await session.commit()
            print(f"Created user {user.id}")
        else:
            print(f"Found User ID: {user.id}")

        target_user_id = user.id
        print(f"Testing with User ID: {target_user_id}")
        
        # Insert Action (Drink Water) - 15 minutes ago
        past_time = datetime.now() - timedelta(minutes=15)
        action = UserActionLog(
            user_id=target_user_id,
            action="drink_water",
            object="test_glass",
            timestamp=past_time
        )
        session.add(action)
        await session.commit()
        print(f"Inserted 'drink_water' action at {past_time} (15 mins ago).")
        return target_user_id

async def verify_notification(user_id):
    """Verify notification was saved."""
    print("Verifying notification persistence...")
    async with db.async_session_maker() as session:
        query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
        result = await session.execute(query)
        notification = result.scalars().first()
        if notification:
            print(f"SUCCESS: Notification found! ID={notification.id}, Title='{notification.title}', Content='{notification.content}'")
        else:
            print("FAILURE: No notification found for user.")

async def main():
    try:
        db.init_mysql()
        # Mock Milvus Init (or it will fail if real milvus is not reachable, but user said it works)
        # Verify script calls `db.init_mysql()` but not milvus.
        # However, `hydration.py` initializes MilvusService.
        # We should try to init milvus or patch it if we want to run this offline.
        # But User said "milvus已经接通并有数据", so we assume it works.
        # BUT, `init_databases` is not called here. `hydration.py` calls `MilvusService()` which calls `init_milvus`.
        # So it should be fine.
        
        await create_tables()
        user_id = await setup_data()
        
        if user_id:
            print(f"Running Check Logic for user {user_id}...")
            await _check_logic(user_id)
            print("Logic Finished. Checking DB...")
            await verify_notification(user_id)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close_mysql()

if __name__ == "__main__":
    asyncio.run(main())
