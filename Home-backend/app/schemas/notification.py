from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class NotificationCategory(str, Enum):
    SYSTEM = "system"
    REMINDER = "reminder"
    ALERT = "alert"

class NotificationBase(BaseModel):
    category: NotificationCategory
    title: str
    content: Optional[str] = None
    is_read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationDTO(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
