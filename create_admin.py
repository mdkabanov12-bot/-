import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.database import SessionLocal, init_db
from models import User, UserRole


def hash_password(password: str) -> str:
    """Хеширование пароля (как в auth.py)"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin():
    """Создать пользователя с ролью администратора"""
    
    # Инициализируем БД (создаём таблицы, если нет)
    init_db()
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже админ
        existing_admin = db.execute(
            select(User).where(User.role == UserRole.admin)
        ).scalars().first()
        
        if existing_admin:
            print("=" * 50)
            print("ADMIN USER ALREADY EXISTS!")
            print("=" * 50)
            print(f"Email:    {existing_admin.email}")
            print(f"Name:     {existing_admin.name}")
            print(f"Role:     {existing_admin.role.value}")
            print("=" * 50)
            print("Use password: Admin@123456")
            print("=" * 50)
            return
        
        # Данные администратора
        admin_name = "Admin"
        admin_email = "admin@example.com"
        admin_password = "Admin@123456"
        
        # Хешируем пароль
        hashed_password = hash_password(admin_password)
        
        # Создаём администратора
        new_admin = User(
            name=admin_name,
            email=admin_email,
            hashed_password=hashed_password,
            role=UserRole.admin
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print("=" * 50)
        print("ADMIN USER CREATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Email:    {admin_email}")
        print(f"Password: {admin_password}")
        print(f"Role:     {UserRole.admin.value}")
        print("=" * 50)
        print("WARNING: Save these credentials in a secure place!")
        print("=" * 50)
        
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
