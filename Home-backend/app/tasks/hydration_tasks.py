"""喝水提醒 Celery 任务模块。

提供定时检查和发送喝水提醒的 Celery 任务。
"""

import logging
from sqlalchemy import select

from app.infrastructure.celery_app import celery_app
from app.core.async_helpers import run_async
from app.services.hydration_service import HydrationService
import app.infrastructure.database as db

logger = logging.getLogger(__name__)


@celery_app.task
def check_hydration_habit_task(user_id: int):
    """检查单个用户的喝水习惯并发送提醒。

    Args:
        user_id: 用户 ID
    """
    logger.info(f"Starting hydration check for user {user_id}")
    try:
        run_async(_check_logic(user_id))
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise


async def _check_logic(user_id: int):
    """异步执行喝水提醒检查。

    Args:
        user_id: 用户 ID
    """
    # 确保数据库已初始化
    if db.async_session_maker is None:
        if not db.engine:
            db.init_mysql()

    async with db.async_session_maker() as session:
        service = HydrationService(session)
        await service.check_and_remind(user_id)


@celery_app.task
def trigger_daily_hydration_checks():
    """触发所有活跃用户的喝水提醒检查。

    此任务由 Celery Beat 定期调用，遍历所有活跃用户
    并为他们触发喝水提醒检查任务。
    """
    try:
        run_async(_trigger_all_users())
    except Exception as e:
        logger.error(f"Trigger task failed: {e}")
        raise


async def _trigger_all_users():
    """异步触发所有用户的喝水提醒检查。"""
    # 确保数据库已初始化
    if db.async_session_maker is None:
        db.init_mysql()

    from app.models.user import User

    async with db.async_session_maker() as session:
        query = select(User.id).where(User.is_active == True)
        result = await session.execute(query)
        user_ids = result.scalars().all()

        for uid in user_ids:
            check_hydration_habit_task.delay(uid)

        logger.info(f"Triggered hydration checks for {len(user_ids)} active users")
