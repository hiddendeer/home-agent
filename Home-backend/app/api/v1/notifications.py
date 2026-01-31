from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from typing import Any, List
import logging

from app.database import get_mysql_session
from app.models.notification import Notification
from app.schemas.notification import NotificationDTO, NotificationCategory
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.get("/", response_model=List[NotificationDTO])
async def read_notifications(
    db: AsyncSession = Depends(get_mysql_session),
    skip: int = 0,
    limit: int = 100,
    category: NotificationCategory = None,
    user_id: int = Query(..., description="User ID") 
) -> Any:
    """
    Retrieve notifications.
    """
    query = select(Notification).where(Notification.user_id == user_id)
    
    if category:
        query = query.where(Notification.category == category)
    
    query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    return notifications

@router.get("/unread-count", response_model=int)
async def get_unread_count(
    db: AsyncSession = Depends(get_mysql_session),
    user_id: int = Query(..., description="User ID")
) -> Any:
    """
    Get unread notification count.
    """
    query = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    result = await db.execute(query)
    return result.scalar() or 0

@router.put("/{notification_id}/read", response_model=NotificationDTO)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_mysql_session),
    user_id: int = Query(..., description="User ID") 
) -> Any:
    """
    Mark a notification as read.
    """
    result = await db.execute(select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ))
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification

@router.put("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_mysql_session),
    user_id: int = Query(..., description="User ID")
) -> Any:
    """
    Mark all notifications as read.
    """
    stmt = update(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).values(is_read=True)
    
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}
