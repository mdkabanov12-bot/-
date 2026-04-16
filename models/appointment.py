from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from database.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    cancelled = Column(Boolean, default=False, nullable=False, index=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Связи
    user = relationship("User", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, user_id={self.user_id}, service_id={self.service_id}, cancelled={self.cancelled})>"
