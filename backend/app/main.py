from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
import app.models  # noqa: F401 - registers all tables on Base.metadata
import sqlalchemy.exc

from app.models.core import User
from app.models.enums import UserRole, UserStatus

from app.routers import (
    auth, employees, customers, destinations, membership, rooms, restaurant,
    party_hall, pool, spa, club, laundry, bookings, billing, dashboard, reports,
    gallery, contact, content, notifications,
)

app = FastAPI(
    title="Hotel & Restaurant Management System API",
    description="CST-HRM-001 — CoreStone Technologies",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth.router, employees.router, customers.router, destinations.router, membership.router,
    rooms.router, restaurant.router, party_hall.router, pool.router, spa.router, club.router,
    laundry.router, bookings.router, billing.router, dashboard.router, reports.router,
    gallery.router, contact.router, content.router, notifications.router,
):
    app.include_router(router)


@app.on_event("startup")
def on_startup():

    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            admin = User(
                username=settings.SEED_ADMIN_USERNAME,
                hashed_password=hash_password(settings.SEED_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )
            db.add(admin)
            db.commit()
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError):
        # Database tables might not be created yet, so skip seeding.
        pass
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": "Hotel & Restaurant Management System API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
