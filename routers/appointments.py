from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_appointments():
    """Получить все записи"""
    return {"message": "Appointments endpoint - TODO"}


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: int):
    """Получить запись по ID"""
    return {"message": f"Appointment {appointment_id} - TODO"}


@router.post("/")
async def create_appointment():
    """Создать запись"""
    return {"message": "Create appointment - TODO"}


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: int):
    """Обновить запись"""
    return {"message": f"Update appointment {appointment_id} - TODO"}


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Удалить запись"""
    return {"message": f"Delete appointment {appointment_id} - TODO"}
