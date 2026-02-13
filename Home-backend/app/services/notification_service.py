"""通知服务模块。

提供通知创建、查询、更新等业务逻辑。
"""

import logging
from datetime import datetime
from sqlalchemy import select, desc, func
from typing import List

from app.models.notification import Notification
from app.schemas.notification import NotificationCategory

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务类。

    封装通知相关的业务逻辑，包括：
    - 创建通知
    - 查询通知
    - 标记通知为已读
    - 获取未读数量
    """

    def __init__(self, db_session):
        """初始化通知服务。

        Args:
            db_session: 异步数据库会话
        """
        self.db = db_session

    async def create_notification(
        self,
        user_id: int,
        category: NotificationCategory,
        title: str,
        content: str,
        created_at: datetime | None = None
    ) -> Notification:
        """创建新通知。

        Args:
            user_id: 用户 ID
            category: 通知类别
            title: 通知标题
            content: 通知内容
            created_at: 创建时间（默认为当前时间）

        Returns:
            创建的通知对象
        """
        if created_at is None:
            created_at = datetime.now()

        notification = Notification(
            user_id=user_id,
            category=category.value,
            title=title,
            content=content,
            is_read=False,
            created_at=created_at
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        logger.info(
            f"Notification created: id={notification.id}, "
            f"user_id={user_id}, category={category.value}"
        )
        return notification

    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category: NotificationCategory | None = None
    ) -> List[Notification]:
        """获取用户的通知列表。

        Args:
            user_id: 用户 ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            category: 可选的通知类别筛选

        Returns:
            通知列表
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if category:
            query = query.where(Notification.category == category.value)

        query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return notifications

    async def get_unread_count(self, user_id: int) -> int:
        """获取用户未读通知数量。

        Args:
            user_id: 用户 ID

        Returns:
            未读通知数量
        """
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> Notification | None:
        """标记通知为已读。

        Args:
            notification_id: 通知 ID
            user_id: 用户 ID

        Returns:
            更新后的通知对象，如果通知不存在则返回 None
        """
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        result = await self.db.execute(query)
        notification = result.scalars().first()

        if notification:
            notification.is_read = True
            await self.db.commit()
            await self.db.refresh(notification)
            logger.info(f"Notification marked as read: id={notification_id}")

        return notification

    async def mark_all_as_read(self, user_id: int) -> int:
        """标记用户所有通知为已读。

        Args:
            user_id: 用户 ID

        Returns:
            更新的记录数
        """
        from sqlalchemy import update

        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)

        result = await self.db.execute(stmt)
        await self.db.commit()

        updated_count = result.rowcount
        logger.info(
            f"Marked all notifications as read: user_id={user_id}, "
            f"count={updated_count}"
        )
        return updated_count
