"""喝水提醒服务模块。

提供喝水提醒检查和通知创建等业务逻辑。
"""

import logging
from datetime import datetime
from sqlalchemy import select, desc

from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCategory
from app.utils.datetime import calculate_minutes_ago

logger = logging.getLogger(__name__)


class HydrationService:
    """喝水提醒服务类。

    封装喝水提醒相关的业务逻辑，包括：
    - 检查用户是否需要喝水提醒
    - 创建喝水提醒通知
    - 更新用户最后提醒时间
    """

    def __init__(self, db_session):
        """初始化喝水提醒服务。

        Args:
            db_session: 异步数据库会话
        """
        self.db = db_session

    async def check_and_remind(self, user_id: int, now: datetime | None = None) -> bool:
        """检查用户是否需要喝水提醒，如果需要则发送提醒。

        实现精确的10小时提醒逻辑：
        - 用户喝水后10小时时发送提醒
        - 使用595-605分钟的检查窗口，确保在精确的10小时时提醒
        - 防止重复提醒（距离上次提醒至少590分钟）

        Args:
            user_id: 用户 ID
            now: 当前时间（默认使用系统当前时间）

        Returns:
            是否发送了提醒
        """
        if now is None:
            now = datetime.now()

        # 1. 获取用户上次喝水时间和上次提醒时间
        last_drink_time = await self._get_last_drink_time(user_id)
        last_remind_time = await self._get_last_remind_time(user_id)

        # 计算距离上次喝水的分钟数
        minutes_since = 9999  # 默认：首次使用或很久未使用
        if last_drink_time:
            minutes_since = calculate_minutes_ago(last_drink_time, now)

        # 计算距离上次提醒的分钟数
        minutes_since_last_remind = 9999
        if last_remind_time:
            minutes_since_last_remind = calculate_minutes_ago(last_remind_time, now)

        # 2. 循环提醒逻辑：每10小时检查一次并发送提醒
        # 触发条件：
        #   - 距离上次喝水 >= 600分钟（10小时）
        #   - 距离上次提醒 >= 590分钟（防止重复提醒，10小时内只提醒一次）
        # 这样可以实现：喝水10小时后提醒，之后每10小时循环提醒，直到用户喝水
        should_remind = minutes_since >= 600 and minutes_since_last_remind >= 590

        logger.info(
            f"User {user_id} hydration check: "
            f"last_drink={last_drink_time} ({minutes_since:.1f}m ago), "
            f"last_remind={last_remind_time} ({minutes_since_last_remind:.1f}m ago), "
            f"should_remind={should_remind}"
        )

        # 3. 如果需要提醒，创建通知并更新最后提醒时间
        if should_remind:
            await self._create_reminder(user_id, now)
            logger.info(f"Hydration reminder sent to user {user_id} at {now}")
            return True
        else:
            logger.debug(
                f"User {user_id} no reminder needed "
                f"(last drink {minutes_since:.1f}m ago)"
            )
            return False

    async def _get_last_drink_time(self, user_id: int) -> datetime | None:
        """获取用户最后一次喝水时间。

        Args:
            user_id: 用户 ID

        Returns:
            最后喝水时间或 None
        """
        from app.models.behavior import Behavior

        query = select(Behavior).where(
            Behavior.user_id == user_id,
            Behavior.action_type == "drink_water"
        ).order_by(desc(Behavior.timestamp)).limit(1)

        result = await self.db.execute(query)
        last_action = result.scalars().first()
        return last_action.timestamp if last_action else None

    async def _get_last_remind_time(self, user_id: int) -> datetime | None:
        """获取用户上次喝水提醒时间。

        Args:
            user_id: 用户 ID

        Returns:
            上次提醒时间或 None
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        return user.last_hydration_remind_at if user else None

    async def _create_reminder(self, user_id: int, now: datetime) -> None:
        """创建喝水提醒通知并更新用户最后提醒时间。

        Args:
            user_id: 用户 ID
            now: 当前时间
        """
        title = "饮水提醒"
        content = "温馨提醒：您已经10小时没喝水了，请记得补水哦！"

        # 创建通知
        notification = Notification(
            user_id=user_id,
            category=NotificationCategory.REMINDER.value,
            title=title,
            content=content,
            is_read=False,
            created_at=now
        )
        self.db.add(notification)

        # 更新用户最后提醒时间
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        if user:
            user.last_hydration_remind_at = now

        await self.db.commit()
