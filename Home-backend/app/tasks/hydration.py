import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from app.celery_app import celery_app
from app.config import get_settings
import app.database as db

from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCategory
from app.models.behavior import Behavior

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
    """
    检查用户是否需要喝水提醒。

    实现精确的10小时提醒逻辑：
    - 用户喝水后10小时时发送提醒
    - 使用595-605分钟的检查窗口，确保在精确的10小时时提醒
    - 防止重复提醒（距离上次提醒至少590分钟）
    """
    now = datetime.now()

    # 1. 获取用户上次喝水时间和上次提醒时间
    last_drink_time = None
    last_remind_time = None

    if db.async_session_maker is None:
        if not db.engine:
            db.init_mysql()

    async with db.async_session_maker() as session:
        # 获取最后喝水时间
        query = select(Behavior).where(
            Behavior.user_id == user_id,
            Behavior.action_type == "drink_water"
        ).order_by(desc(Behavior.timestamp)).limit(1)
        result = await session.execute(query)
        last_action = result.scalars().first()
        if last_action:
            last_drink_time = last_action.timestamp

        # 获取上次提醒时间
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalars().first()
        if user and user.last_hydration_remind_at:
            last_remind_time = user.last_hydration_remind_at

    # 计算距离上次喝水的分钟数
    minutes_since = 0
    if last_drink_time:
        if last_drink_time.tzinfo:
            minutes_since = (now.astimezone(last_drink_time.tzinfo) - last_drink_time).total_seconds() / 60
        else:
            minutes_since = (now - last_drink_time).total_seconds() / 60
    else:
        minutes_since = 9999  # 首次使用或很久未使用

    # 计算距离上次提醒的分钟数
    minutes_since_last_remind = 9999
    if last_remind_time:
        if last_remind_time.tzinfo:
            minutes_since_last_remind = (now.astimezone(last_remind_time.tzinfo) - last_remind_time).total_seconds() / 60
        else:
            minutes_since_last_remind = (now - last_remind_time).total_seconds() / 60

    # 2. 动态窗口检查：在595-605分钟（约10小时）之间发送提醒
    # 检查窗口：确保在用户喝水后大约10小时时发送提醒
    # 防重复：距离上次提醒至少590分钟
    in_remind_window = 595 <= minutes_since <= 605
    should_remind = in_remind_window and minutes_since_last_remind >= 590

    logger.info(
        f"User {user_id} hydration check: "
        f"last_drink={last_drink_time} ({minutes_since:.1f}m ago), "
        f"last_remind={last_remind_time} ({minutes_since_last_remind:.1f}m ago), "
        f"in_window={in_remind_window}, should_remind={should_remind}"
    )

    # 3. 如果需要提醒，创建通知并更新最后提醒时间
    if should_remind:
        title = "饮水提醒"
        content = "温馨提醒：您已经10小时没喝水了，请记得补水哦！"

        try:
            async with db.async_session_maker() as session:
                # 创建通知
                notification = Notification(
                    user_id=user_id,
                    category=NotificationCategory.REMINDER.value,
                    title=title,
                    content=content,
                    is_read=False,
                    created_at=now
                )
                session.add(notification)

                # 更新用户最后提醒时间
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                if user:
                    user.last_hydration_remind_at = now

                await session.commit()
                logger.info(f"Hydration reminder sent to user {user_id} at {now}")
        except Exception as e:
            logger.error(f"Failed to save notification/update user: {e}")
    else:
        logger.debug(f"User {user_id} no reminder needed (last drink {minutes_since:.1f}m ago)")

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
