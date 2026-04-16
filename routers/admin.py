from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from schemas import ServiceResponse, ServiceCreate, ServiceUpdate, NotificationResponse
from models import Service, Appointment, User, Notification

router = APIRouter()


def get_current_user(user_id: int, db: Session):
    """Проверка существования пользователя"""
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


def check_admin(user: User):
    """Проверка роли администратора"""
    if user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуется роль администратора"
        )


@router.post("/admin/services/cleanup-completed")
async def cleanup_completed_services(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить все завершённые услуги (только админ)"""
    # Проверка администратора
    user = get_current_user(user_id, db)
    check_admin(user)
    
    now = datetime.now()
    
    # Находим все услуги, которые закончились
    services = db.execute(select(Service)).scalars().all()
    
    deleted_count = 0
    for service in services:
        service_end_time = service.start_time + timedelta(minutes=service.duration_minutes)
        
        # Если услуга закончилась, удаляем её
        if service_end_time <= now:
            # Получаем все активные записи на эту услугу
            appointments = db.execute(
                select(Appointment).where(
                    Appointment.service_id == service.id,
                    Appointment.cancelled == False
                )
            ).scalars().all()
            
            # Отправляем уведомления пользователям
            for appointment in appointments:
                appointment_user = db.execute(
                    select(User).where(User.id == appointment.user_id)
                ).scalars().first()
                
                if appointment_user:
                    notification = Notification(
                        user_id=appointment_user.id,
                        message=f"Услуга '{service.name}' завершена. Спасибо за использование!",
                        is_read=False
                    )
                    db.add(notification)
                
                # Помечаем запись как завершённую
                appointment.cancelled = True
                appointment.cancelled_at = now
            
            # Удаляем услугу
            db.delete(service)
            deleted_count += 1
    
    db.commit()
    
    return {
        "message": f"Удалено {deleted_count} завершённых услуг",
        "deleted_count": deleted_count
    }


@router.post("/admin/services", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Создать новую услугу (только админ)"""
    # Проверка администратора
    user = get_current_user(user_id, db)
    check_admin(user)
    
    # Проверяем, не начинается ли услуга в прошлом
    if service.start_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала услуги должно быть в будущем"
        )
    
    # Создаем услугу
    new_service = Service(
        name=service.name,
        duration_minutes=service.duration_minutes,
        start_time=service.start_time,
        created_by=user.id
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return ServiceResponse(
        id=new_service.id,
        name=new_service.name,
        start_time=new_service.start_time,
        duration_minutes=new_service.duration_minutes,
        created_by=new_service.created_by,
        booked_users=[]
    )


@router.put("/admin/services/{service_id}/time", response_model=ServiceResponse)
async def update_service_time(
    service_id: int,
    new_start_time: datetime,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Изменить время начала услуги (только админ, только на будущее)"""
    # Проверка администратора
    user = get_current_user(user_id, db)
    check_admin(user)
    
    # Проверяем, не начинается ли услуга в прошлом
    if new_start_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала услуги должно быть в будущем"
        )

    # Находим услугу
    service = db.execute(
        select(Service).where(Service.id == service_id)
    ).scalars().first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Проверяем, не идёт ли услуга сейчас
    service_end_time = service.start_time + timedelta(minutes=service.duration_minutes)
    if service.start_time <= datetime.now() <= service_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить время услуги, которая уже идёт. Дождитесь окончания услуги."
        )
    
    # Получаем всех активных пользователей, записанных на эту услугу
    active_appointments = db.execute(
        select(Appointment).where(
            Appointment.service_id == service_id,
            Appointment.cancelled == False
        )
    ).scalars().all()
    
    # Если есть пользователи, отправляем уведомления
    if active_appointments:
        for appointment in active_appointments:
            # Находим пользователя
            appointment_user = db.execute(
                select(User).where(User.id == appointment.user_id)
            ).scalars().first()
            
            if appointment_user:
                # Создаем уведомление о переносе времени
                old_time = service.start_time.strftime("%d.%m.%Y %H:%M")
                new_time = new_start_time.strftime("%d.%m.%Y %H:%M")
                
                notification = Notification(
                    user_id=appointment_user.id,
                    message=f"Время услуги '{service.name}' перенесено с {old_time} на {new_time}",
                    is_read=False
                )
                db.add(notification)
    
    # Обновляем время услуги
    service.start_time = new_start_time
    db.commit()
    db.refresh(service)
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        start_time=service.start_time,
        duration_minutes=service.duration_minutes,
        created_by=service.created_by,
        booked_users=[]
    )


@router.get("/admin/services/{service_id}/users", response_model=List[dict])
async def get_service_users(
    service_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить список пользователей, записанных на услугу (только админ)"""
    # Проверка администратора
    user = get_current_user(user_id, db)
    check_admin(user)
    
    # Проверяем существование услуги
    service = db.execute(
        select(Service).where(Service.id == service_id)
    ).scalars().first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Получаем все записи на эту услугу
    appointments = db.execute(
        select(Appointment).where(Appointment.service_id == service_id)
    ).scalars().all()
    
    # Формируем список пользователей
    result = []
    for appointment in appointments:
        user_data = db.execute(
            select(User).where(User.id == appointment.user_id)
        ).scalars().first()
        
        if user_data:
            result.append({
                "user_id": user_data.id,
                "user_name": user_data.name,
                "user_email": user_data.email,
                "appointment_id": appointment.id,
                "cancelled": appointment.cancelled,
                "cancelled_at": appointment.cancelled_at
            })
    
    return result


@router.delete("/admin/services/{service_id}")
async def delete_service(
    service_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить услугу и все связанные записи (только админ)"""
    
    # Проверка администратора
    user = get_current_user(user_id, db)
    check_admin(user)
    
    # Находим услугу
    service = db.execute(
        select(Service).where(Service.id == service_id)
    ).scalars().first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Проверяем, не идёт ли услуга сейчас
    service_end_time = service.start_time + timedelta(minutes=service.duration_minutes)
    if service.start_time <= datetime.now() <= service_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить услугу, которая уже идёт. Дождитесь окончания услуги."
        )
    
    # Получаем все записи на эту услугу
    appointments = db.execute(
        select(Appointment).where(Appointment.service_id == service_id)
    ).scalars().all()
    
    # Отправляем уведомления и помечаем записи как отменённые
    for appointment in appointments:
        # Находим пользователя
        appointment_user = db.execute(
            select(User).where(User.id == appointment.user_id)
        ).scalars().first()
        
        if appointment_user:
            # Создаем уведомление об отмене услуги
            notification = Notification(
                user_id=appointment_user.id,
                message=f"Услуга '{service.name}' была отменена администратором. Ваша запись отменена.",
                is_read=False
            )
            db.add(notification)
        
        # Помечаем запись как отменённую (если ещё не отменена)
        if not appointment.cancelled:
            appointment.cancelled = True
            appointment.cancelled_at = datetime.now()
    
    # Удаляем услугу (каскадное удаление сработает для записей, если настроено)
    db.delete(service)
    db.commit()
    
    return {
        "message": f"Услуга '{service.name}' и {len(appointments)} связанных записей успешно удалены",
        "service_id": service_id
    }
