from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class NotificationType(str, Enum):
    START_REMINDER = "start_reminder"
    CANCELLATION = "cancellation"
    OTHER = "other"


# === User Schemas ===
class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.user


class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True


# === Service Schemas ===
class ServiceBase(BaseModel):
    name: str
    duration_minutes: int
    start_time: datetime


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = None
    duration_minutes: int | None = None
    start_time: datetime | None = None


class ServiceResponse(ServiceBase):
    id: int
    created_by: int
    booked_users: list[int] = []

    class Config:
        from_attributes = True


class BookAppointmentRequest(BaseModel):
    user_id: int


# === Appointment Schemas ===
class AppointmentStatus(str, Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    cancelled = "cancelled"
    completed = "completed"


class AppointmentBase(BaseModel):
    service_id: int


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    service_id: int
    cancelled: bool
    cancelled_at: Optional[datetime]
    service_name: str
    service_start_time: datetime
    service_duration_minutes: int
    status: AppointmentStatus

    class Config:
        from_attributes = True


# === Notification Schemas ===
class NotificationBase(BaseModel):
    message: str


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    notification_type: Optional[str] = None

    class Config:
        from_attributes = True
