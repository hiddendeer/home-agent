from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class UserActionLog(Base):
    """User action log model."""

    __tablename__ = "user_action_logs"

    id = Column(Integer, primary_key=True, index=True, comment="Log ID")
    user_id = Column(Integer, index=True, nullable=False, comment="User ID")
    action = Column(String(100), index=True, nullable=False, comment="Action type (e.g., drink_water)")
    object = Column(String(100), nullable=True, comment="Object acted upon")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), comment="Action time")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Record creation time")

    def __repr__(self) -> str:
        return f"<UserActionLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
