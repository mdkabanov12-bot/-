from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import Notification


router = APIRouter()


@router.get("/")
async def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить все уведомления пользователя"""
    notifications = db.execute(
        select(Notification).where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    ).scalars().all()
    
    return notifications


@router.get("/{notification_id}")
async def get_notification(
    notification_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить уведомление по ID"""
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).scalars().first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    return notification


@router.post("/")
async def create_notification(
    user_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """Создать уведомление"""
    notification = Notification(
        user_id=user_id,
        message=message
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.put("/{notification_id}")
async def update_notification(
    notification_id: int,
    user_id: int,
    message: str | None = None,
    is_read: bool | None = None,
    db: Session = Depends(get_db)
):
    """Обновить уведомление"""
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).scalars().first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    if message is not None:
        notification.message = message
    if is_read is not None:
        notification.is_read = is_read
    
    db.commit()
    db.refresh(notification)
    
    return notification


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить уведомление"""
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    ).scalars().first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Уведомление успешно удалено", "notification_id": notification_id}
