from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.infrastructure.database import Base

class Notification(Base):
    """Notification model for Message Center."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, comment="Notification ID")
    user_id = Column(Integer, index=True, nullable=False, comment="User ID")
    category = Column(String(50), index=True, nullable=False, comment="Category: system, reminder, alert")
    title = Column(String(255), nullable=False, comment="Notification Title")
    content = Column(Text, nullable=True, comment="Notification Content")
    is_read = Column(Boolean, default=False, index=True, comment="Is Read")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="Creation Time")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, title={self.title})>"
