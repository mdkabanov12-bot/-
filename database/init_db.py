from database.database import engine, Base
from models import User, Service, Appointment, Notification
from sqlalchemy import inspect


def create_tables():
    """Создать все таблицы в базе данных"""
    # Проверяем, нужны ли изменения
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Создаем/обновляем таблицы
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы/обновлены!")
    
    # Информируем о новых полях
    if "services" in existing_tables:
        print("  - Service: добавлено поле notified_start")
    if "notifications" in existing_tables:
        print("  - Notification: добавлено поле notification_type")


if __name__ == "__main__":
    create_tables()
