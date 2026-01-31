from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserActionBase(BaseModel):
    user_id: int
    action: str
    object: Optional[str] = None
    timestamp: Optional[datetime] = None

class UserActionCreate(UserActionBase):
    pass

class UserAction(UserActionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
