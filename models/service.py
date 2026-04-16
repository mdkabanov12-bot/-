from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, validates

from database.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notified_start = Column(Boolean, default=False, nullable=False)

    # Связи
    created_by_user = relationship("User", back_populates="services")
    appointments = relationship("Appointment", back_populates="service", cascade="all, delete-orphan")

    @property
    def booked_users(self):
        """Возвращает список ID записанных пользователей"""
        if self.appointments:
            return [apt.user_id for apt in self.appointments if not apt.cancelled]
        return []

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', duration={self.duration_minutes}min)>"
