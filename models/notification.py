from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base
from schemas import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    notification_type = Column(String(50), default=NotificationType.OTHER.value, nullable=False, index=True)

    # Связи
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, is_read={self.is_read})>"
