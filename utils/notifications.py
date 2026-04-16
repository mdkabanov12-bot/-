from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Notification, Appointment, Service
from schemas import NotificationType


def check_and_send_start_notifications(user_id: int, db: Session):
    """
    Проверяет и отправляет уведомления о начале услуг.
    Вызывается при запросе /my/appointments или /notifications/unread
    """
    now = datetime.now()
    
    # Получаем все активные записи пользователя
    appointments = db.execute(
        select(Appointment).where(
            Appointment.user_id == user_id,
            Appointment.cancelled == False
        )
    ).scalars().all()
    
    for appointment in appointments:
        # Получаем услугу
        service = db.execute(
            select(Service).where(Service.id == appointment.service_id)
        ).scalars().first()
        
        if not service:
            continue
        
        # Проверяем: не была ли услуга уже уведомлена
        if service.notified_start:
            continue
        
        # Проверяем: находится ли текущее время в диапазоне начала услуги
        start_time = service.start_time
        end_time = datetime.fromtimestamp(
            start_time.timestamp() + service.duration_minutes * 60
        )
        
        # Если услуга началась или должна была начаться (в пределах 5 минут после начала)
        if start_time <= now <= end_time:
            # Отправляем уведомление
            notification = Notification(
                user_id=user_id,
                message=f"Услуга '{service.name}' началась в {start_time.strftime('%H:%M')}",
                is_read=False,
                notification_type=NotificationType.START_REMINDER.value
            )
            db.add(notification)
            
            # Помечаем услугу как уведомлённую
            service.notified_start = True
            
            db.commit()
