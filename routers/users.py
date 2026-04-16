from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    """Получить всех пользователей"""
    return {"message": "Users endpoint - TODO"}


@router.get("/{user_id}")
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    return {"message": f"User {user_id} - TODO"}


@router.post("/")
async def create_user():
    """Создать пользователя"""
    return {"message": "Create user - TODO"}


@router.put("/{user_id}")
async def update_user(user_id: int):
    """Обновить пользователя"""
    return {"message": f"Update user {user_id} - TODO"}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Удалить пользователя"""
    return {"message": f"Delete user {user_id} - TODO"}
