from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from schemas import NotificationResponse
from models import Notification, User, Appointment, Service
from utils.notifications import check_and_send_start_notifications

router = APIRouter()


@router.get("/notifications/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить все непрочитанные уведомления пользователя"""
    # Сначала проверяем и отправляем уведомления о начале услуг
    check_and_send_start_notifications(user_id, db)
    
    # Получаем непрочитанные уведомления
    notifications = db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc())
    ).scalars().all()
    
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at
        )
        for n in notifications
    ]


@router.post("/notifications/mark-read")
async def mark_notifications_as_read(
    user_id: int,
    notification_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Пометить уведомления как прочитанные (массово или все)"""
    # Если переданы конкретные ID — помечаем только их
    if notification_ids:
        notifications = db.execute(
            select(Notification).where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).scalars().all()
    else:
        # Если ID не переданы — помечаем все непрочитанные
        notifications = db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).scalars().all()
    
    if not notifications:
        return {"message": "Нет непрочитанных уведомлений для отметки", "count": 0}
    
    for notification in notifications:
        notification.is_read = True
    
    db.commit()
    
    return {
        "message": f"Помечено как прочитанные: {len(notifications)} уведомлений",
        "count": len(notifications)
    }

