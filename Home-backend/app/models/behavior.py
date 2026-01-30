from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Behavior(Base):
    """用户行为表模型。"""

    __tablename__ = "behaviors"

    id = Column(Integer, primary_key=True, index=True, comment="行为记录ID")
    user_id = Column(Integer, index=True, nullable=False, comment="用户ID")
    device_id = Column(String(100), index=True, nullable=False, comment="设备ID")
    action_type = Column(String(50), index=True, nullable=False, comment="动作类型")
    details = Column(JSON, nullable=True, comment="原始细节数据")
    raw_content = Column(Text, nullable=True, comment="原始文本描述")
    semantic_content = Column(Text, nullable=True, comment="语义化后的描述")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), comment="发生时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="入库时间")

    def __repr__(self) -> str:
        return f"<Behavior(id={self.id}, user_id={self.user_id}, action_type={self.action_type})>"
