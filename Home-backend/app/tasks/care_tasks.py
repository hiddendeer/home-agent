"""深夜回家关怀任务模块。"""

import logging
from datetime import datetime
from app.infrastructure.celery_app import celery_app
from app.core.async_helpers import run_async
from app.models.notification import Notification
from app.models.behavior import Behavior
from app.schemas.notification import NotificationCategory
import app.infrastructure.database as db

logger = logging.getLogger(__name__)

@celery_app.task
def send_late_night_care_notification(user_id: int):
    """发送深夜回家关怀通知。"""
    logger.info(f"Triggering late night care notification for user {user_id}")
    try:
        run_async(_send_care_logic(user_id))
    except Exception as e:
        logger.error(f"Failed to send care notification: {e}")
        raise

async def _send_care_logic(user_id: int):
    """异步执行关怀通知逻辑。"""
    logger.info(f"Executing _send_care_logic for user_id={user_id}")
    if db.async_session_maker is None:
        db.init_mysql()

    async with db.async_session_maker() as session:
        # 1. 创建通知
        title = "回家关怀"
        content = "陈先生，检测到您深夜回家，空调为您开启，请注意休息。"
        
        notification = Notification(
            user_id=user_id,
            category=NotificationCategory.REMINDER.value,
            title=title,
            content=content,
            is_read=False,
            created_at=datetime.now()
        )
        session.add(notification)
        logger.info(f"Notification added to session for user_id={user_id}")
        
        # 2. 模拟自动开启空调的行为记录
        ac_behavior = Behavior(
            user_id=user_id,
            device_id="ac",
            action_type="toggle_ac",
            details={"status": "on", "temperature": 24, "mode": "auto", "reason": "late_night_return"},
            raw_content="系统为您自动开启了空调，设定的温度为 24°C",
            semantic_content="管家检测到您深夜回家，已为您自动开启空调并调至24°C。"
        )
        session.add(ac_behavior)
        logger.info(f"AC behavior added to session for user_id={user_id}")
        
        await session.commit()
        logger.info(f"Care logic committed successfully for user_id={user_id}")
