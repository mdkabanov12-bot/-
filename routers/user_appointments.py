from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from schemas import (
    ServiceResponse, AppointmentResponse, AppointmentStatus, BookAppointmentRequest, NotificationType
)
from models import Service, Appointment, User, Notification
from utils.notifications import check_and_send_start_notifications

router = APIRouter()


def get_appointment_status(service_start_time: datetime, duration_minutes: int, cancelled: bool) -> AppointmentStatus:
    """Вычисляет статус записи на основе времени"""
    if cancelled:
        return AppointmentStatus.cancelled
    
    now = datetime.now()
    start = service_start_time
    end = datetime.fromtimestamp(start.timestamp() + duration_minutes * 60)
    
    if now < start:
        return AppointmentStatus.upcoming
    elif now >= end:
        return AppointmentStatus.completed
    else:
        return AppointmentStatus.ongoing


@router.get("/services")
async def get_available_services(db: Session = Depends(get_db)):
    """Получить список всех доступных услуг"""
    # Получаем все услуги
    services = db.execute(select(Service)).scalars().all()
    
    result = []
    for service in services:
        # Получаем список записанных пользователей для этой услуги
        appointments = db.execute(
            select(Appointment).where(
                Appointment.service_id == service.id,
                Appointment.cancelled == False
            )
        ).scalars().all()
        
        booked_users = [apt.user_id for apt in appointments]
        
        service_data = {
            "id": service.id,
            "name": service.name,
            "start_time": service.start_time,
            "duration_minutes": service.duration_minutes,
            "created_by": service.created_by,
            "booked_users": booked_users
        }
        result.append(service_data)
    
    return result


@router.post("/services/{service_id}/book", response_model=AppointmentResponse)
async def book_service(
    service_id: int,
    request: BookAppointmentRequest,
    db: Session = Depends(get_db)
):
    """Записать пользователя на услугу"""
    # Проверяем существование услуги
    service = db.execute(
        select(Service).where(Service.id == service_id)
    ).scalars().first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Проверяем существование пользователя
    user = db.execute(
        select(User).where(User.id == request.user_id)
    ).scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    now = datetime.now()
    
    # Проверяем, не началась ли услуга
    if service.start_time <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга уже началась или не может быть забронирована"
        )
    
    # Проверяем, не забронирован ли уже пользователь на эту услугу
    existing_appointment = db.execute(
        select(Appointment).where(
            Appointment.service_id == service_id,
            Appointment.user_id == request.user_id,
            Appointment.cancelled == False
        )
    ).scalars().first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны на эту услугу"
        )
    
    # Создаем запись
    appointment = Appointment(
        user_id=request.user_id,
        service_id=service_id,
        cancelled=False
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Возвращаем ответ с информацией об услуге
    return AppointmentResponse(
        id=appointment.id,
        user_id=appointment.user_id,
        service_id=appointment.service_id,
        cancelled=appointment.cancelled,
        cancelled_at=appointment.cancelled_at,
        service_name=service.name,
        service_start_time=service.start_time,
        service_duration_minutes=service.duration_minutes,
        status=get_appointment_status(service.start_time, service.duration_minutes, False)
    )


@router.get("/my/appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить список записей пользователя (активные, без закончившихся)"""
    # Проверяем и отправляем уведомления о начале услуг
    check_and_send_start_notifications(user_id, db)
    
    # Получаем записи пользователя, где cancelled = False
    appointments = db.execute(
        select(Appointment).where(
            Appointment.user_id == user_id,
            Appointment.cancelled == False
        )
    ).scalars().all()
    
    result = []
    for appointment in appointments:
        service = db.execute(
            select(Service).where(Service.id == appointment.service_id)
        ).scalars().first()
        
        if not service:
            continue
        
        status = get_appointment_status(
            service.start_time, 
            service.duration_minutes, 
            appointment.cancelled
        )
        
        # Скрываем закончившиеся записи
        if status == AppointmentStatus.completed:
            continue
        
        result.append(AppointmentResponse(
            id=appointment.id,
            user_id=appointment.user_id,
            service_id=appointment.service_id,
            cancelled=appointment.cancelled,
            cancelled_at=appointment.cancelled_at,
            service_name=service.name,
            service_start_time=service.start_time,
            service_duration_minutes=service.duration_minutes,
            status=status
        ))
    
    return result


@router.delete("/my/appointments/{service_id}")
async def cancel_appointment(
    service_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отменить запись (только если статус 'upcoming')"""
    # Находим запись
    appointment = db.execute(
        select(Appointment).where(
            Appointment.service_id == service_id,
            Appointment.user_id == user_id,
            Appointment.cancelled == False
        )
    ).scalars().first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    # Получаем информацию об услуге
    service = db.execute(
        select(Service).where(Service.id == service_id)
    ).scalars().first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Проверяем статус
    status = get_appointment_status(
        service.start_time, 
        service.duration_minutes, 
        False
    )
    
    if status != AppointmentStatus.upcoming:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отменить можно только будущие записи (статус 'upcoming')"
        )
    
    # Отменяем запись
    appointment.cancelled = True
    from datetime import datetime
    appointment.cancelled_at = datetime.now()
    
    db.commit()
    
    return {"message": "Запись успешно отменена", "appointment_id": appointment.id}
