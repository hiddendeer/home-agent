import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from app.celery_app import celery_app
from app.config import get_settings
import app.database as db
from app.models.action import UserActionLog
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCategory
from app.services.llm_service import LLMService
# Import Milvus Service
from app.services.milvus_service import MilvusService

logger = logging.getLogger(__name__)
settings = get_settings()

def _run_async(coro):
    """
    Helper to run async code in Celery tasks.
    Handles event loop creation/cleanup properly.
    """
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running (rare case), create a new one in a thread
            import concurrent.futures
            import threading

            result = [None]
            exception = [None]

            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(coro)
                except Exception as e:
                    exception[0] = e
                finally:
                    new_loop.close()

            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            thread.join()

            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            # Existing loop but not running, use it
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No loop exists, create new one (standard case for Celery)
        return asyncio.run(coro)

async def _check_logic(user_id: int):
    """Async logic for checking hydration habit with strict 10-min rule."""
    now = datetime.now()
    
    # 1. Check Last Drink Time from MySQL
    last_drink_time = None
    if db.async_session_maker is None:
        if not db.engine:
            db.init_mysql()

    async with db.async_session_maker() as session:
        query = select(UserActionLog).where(
            UserActionLog.user_id == user_id,
            UserActionLog.action == "drink_water"
        ).order_by(desc(UserActionLog.timestamp)).limit(1)
        result = await session.execute(query)
        last_action = result.scalars().first()
        if last_action:
            last_drink_time = last_action.timestamp

    # Calculate time since last drink
    minutes_since = 0
    if last_drink_time:
        # Ensure timezone awareness compatibility if needed, but assuming naive/local match for now
        # If timestamp is timezone aware, make 'now' aware or strip tz. 
        # MySQL datetime usually returns naive if not configured otherwise.
        if last_drink_time.tzinfo:
            minutes_since = (now.astimezone(last_drink_time.tzinfo) - last_drink_time).total_seconds() / 60
        else:
            minutes_since = (now - last_drink_time).total_seconds() / 60
    else:
        minutes_since = 9999 # First time or long time ago

    # 2. Query Milvus for Context (Real Data)
    milvus_context = "No historical context found."
    try:
        milvus = MilvusService()
        # Create a dummy query vector (zeros) since we don't have an embedding model running here easily
        # In a real scenario, we would embed "drinking water habit"
        # For now, we search for *any* vector to get *some* user context
        query_vector = [0.1] * milvus.dim 
        results = await milvus.search_behavior(user_id, query_vector, limit=3)
        if results:
            context_list = [f"- [{datetime.fromtimestamp(r['timestamp'])}] {r['content']}" for r in results]
            milvus_context = "\n".join(context_list)
    except Exception as e:
        logger.warning(f"Milvus query failed (non-critical): {e}")

    # 3. LLM Decision
    llm = LLMService(settings)
    
    prompt = (
        f"Context: strict 10-minute hydration rule.\n"
        f"Current Time: {now}\n"
        f"Last Drink Time: {last_drink_time} ({int(minutes_since)} minutes ago)\n\n"
        f"User Behavior History (from Milvus):\n{milvus_context}\n\n"
        f"Task: strict rule says a user MUST drink water every 10 minutes.\n"
        f"Analyze: Has it been more than 10 minutes? If so, we MUST remind.\n"
        f"Decision: Should we send a reminder? Answer YES or NO. If YES, provide a friendly Chinese reminder message."
    )

    try:
        response = await llm.generate(prompt)
        logger.info(f"LLM Response for user {user_id}: {response}")
        should_remind = "YES" in response.upper()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        # Fallback: Remind if > 10 mins rigid check
        should_remind = minutes_since > 10

    # 4. Push Notification
    if should_remind:
        # Extract message from LLM or use default
        content = response if 'response' in locals() and response else "温馨提醒：您已经超过10分钟没喝水了，请记得补水哦！"
        # If LLM says "YES. 消息...", try to clean it up? 
        # For now, just use the full response as it's usually conversational.
        
        title = "饮水提醒"
        
        # A. Save to DB
        try:
            async with db.async_session_maker() as session:
                notification = Notification(
                    user_id=user_id,
                    category=NotificationCategory.REMINDER.value,
                    title=title,
                    content=content,
                    is_read=False,
                    created_at=now
                )
                session.add(notification)
                await session.commit()
        except Exception as e:
            logger.error(f"DB save failed: {e}")

    else:
        logger.info(f"User {user_id} is hydrated (Last drink {int(minutes_since)} mins ago).")

@celery_app.task
def check_hydration_habit_task(user_id: int):
    """Celery task."""
    logger.info(f"Starting hydration check for user {user_id}")
    try:
        _run_async(_check_logic(user_id))
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise

async def _trigger_all_users():
    """Async trigger."""
    if db.async_session_maker is None:
         db.init_mysql() # Ensure init

    async with db.async_session_maker() as session:
        query = select(User.id).where(User.is_active == True)
        result = await session.execute(query)
        user_ids = result.scalars().all()
        
        for uid in user_ids:
            check_hydration_habit_task.delay(uid)

@celery_app.task
def trigger_daily_hydration_checks():
    """Trigger Checks."""
    try:
        _run_async(_trigger_all_users())
    except Exception as e:
        logger.error(f"Trigger task failed: {e}")
        raise
