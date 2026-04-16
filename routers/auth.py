from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
import hashlib

from database import get_db
from models import User, UserRole
from schemas import UserResponse, UserCreate

router = APIRouter()

# Простая реализация хеширования (в продакшене использовать bcrypt!)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


# Простая реализация токенов (в продакшене использовать JWT!)
def create_access_token(user_id: int, expires_delta: timedelta = timedelta(hours=24)) -> str:
    expires = datetime.now() + expires_delta
    token_data = f"{user_id}:{expires.timestamp()}"
    return hashlib.sha256(token_data.encode()).hexdigest()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из токена"""
    # В реальной реализации нужно декодировать JWT токен
    # Здесь упрощённая версия - ищем пользователя по ID
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    user_role: str


@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Зарегистрировать нового пользователя"""
    # Проверяем, не занят ли email
    existing_user = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    
    # Создаем пользователя
    hashed_password = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Войти в систему (username=email)"""
    # Ищем пользователя по email (username)
    user = db.execute(
        select(User).where(User.email == form_data.username)
    ).scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token = create_access_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_name=user.name,
        user_role=user.role.value
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role
    )
