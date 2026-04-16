from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_services():
    """Получить все услуги"""
    return {"message": "Services endpoint - TODO"}


@router.get("/{service_id}")
async def get_service(service_id: int):
    """Получить услугу по ID"""
    return {"message": f"Service {service_id} - TODO"}


@router.post("/")
async def create_service():
    """Создать услугу"""
    return {"message": "Create service - TODO"}


@router.put("/{service_id}")
async def update_service(service_id: int):
    """Обновить услугу"""
    return {"message": f"Update service {service_id} - TODO"}


@router.delete("/{service_id}")
async def delete_service(service_id: int):
    """Удалить услугу"""
    return {"message": f"Delete service {service_id} - TODO"}
