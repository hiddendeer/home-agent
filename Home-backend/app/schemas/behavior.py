"""行为数据 Schema。"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class BehaviorBase(BaseModel):
    user_id: int = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    action_type: str = Field(..., description="动作类型")
    details: Optional[Dict[str, Any]] = Field(None, description="原始细节数据")
    raw_content: Optional[str] = Field(None, description="原始文本描述")


class BehaviorCreate(BehaviorBase):
    pass


class BehaviorResponse(BehaviorBase):
    id: int
    semantic_content: Optional[str] = None
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class BehaviorQuery(BaseModel):
    user_id: Optional[int] = None
    device_id: Optional[str] = None
    action_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
