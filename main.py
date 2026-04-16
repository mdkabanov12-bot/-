from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import init_db, get_db

# Инициализируем базу данных при запуске приложения
init_db()

app = FastAPI(
    title="FastAPI Project",
    description="Backend for HTML/CSS/JS frontend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI backend"}


# Import and include routers
from routers import users, services, appointments, notifications
from routers import user_appointments, admin, notifications_router, auth

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(notifications_router.router, prefix="/api", tags=["notifications"])
app.include_router(user_appointments.router, prefix="/api", tags=["user-appointments"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications-admin"])
app.include_router(auth.router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)