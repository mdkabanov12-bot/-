from database import engine, Base
from models import Service, Appointment, User  # все модели

def reset_database():
    # Удаляет все таблицы
    Base.metadata.drop_all(bind=engine)
    # Создает заново
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()