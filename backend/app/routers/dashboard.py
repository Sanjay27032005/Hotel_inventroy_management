from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_management
from app.models.core import Employee
from app.models.customer import Customer
from app.models.booking_billing import Booking, Invoice
from app.models.accommodation import Room
from app.models.restaurant import FoodOrder
from app.models.events import EventBooking
from app.models.spa import SpaBooking
from app.models.pool import PoolBooking
from app.models.enums import RoomStatus, PaymentStatus, BookingStatus

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db), _=Depends(require_management)):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = today_start + timedelta(days=1)
    month_start = today.replace(day=1)

    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_employees = db.query(func.count(Employee.id)).scalar() or 0
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0
    todays_bookings = db.query(func.count(Booking.id)).filter(
        Booking.created_at >= today_start, Booking.created_at < today_end
    ).scalar() or 0

    available_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.AVAILABLE).scalar() or 0
    occupied_rooms = db.query(func.count(Room.id)).filter(Room.status == RoomStatus.NOT_AVAILABLE).scalar() or 0

    restaurant_orders_today = db.query(func.count(FoodOrder.id)).filter(
        FoodOrder.created_at >= today_start, FoodOrder.created_at < today_end
    ).scalar() or 0
    spa_sessions_upcoming = db.query(func.count(SpaBooking.id)).filter(
        SpaBooking.booking_date >= today_start, SpaBooking.booking_status == BookingStatus.CONFIRMED
    ).scalar() or 0
    pool_bookings_today = db.query(func.count(PoolBooking.id)).filter(
        PoolBooking.booking_date >= today_start, PoolBooking.booking_date < today_end
    ).scalar() or 0
    upcoming_events = db.query(func.count(EventBooking.id)).filter(
        EventBooking.event_date >= today_start, EventBooking.booking_status == BookingStatus.CONFIRMED
    ).scalar() or 0

    pending_payments = db.query(func.count(Invoice.id)).filter(
        Invoice.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIALLY_PAID])
    ).scalar() or 0

    todays_revenue = db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
        Invoice.payment_status == PaymentStatus.PAID,
        Invoice.created_at >= today_start, Invoice.created_at < today_end,
    ).scalar() or 0
    monthly_revenue = db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
        Invoice.payment_status == PaymentStatus.PAID,
        Invoice.created_at >= datetime.combine(month_start, datetime.min.time()),
    ).scalar() or 0

    return {
        "total_customers": total_customers,
        "total_employees": total_employees,
        "total_bookings": total_bookings,
        "todays_bookings": todays_bookings,
        "available_rooms": available_rooms,
        "occupied_rooms": occupied_rooms,
        "restaurant_orders_today": restaurant_orders_today,
        "spa_sessions_upcoming": spa_sessions_upcoming,
        "pool_bookings_today": pool_bookings_today,
        "upcoming_events": upcoming_events,
        "pending_payments": pending_payments,
        "todays_revenue": float(todays_revenue),
        "monthly_revenue": float(monthly_revenue),
    }


@router.get("/revenue-trend")
def revenue_trend(days: int = 14, db: Session = Depends(get_db), _=Depends(require_management)):
    """Daily revenue for the last N days, for the dashboard's revenue chart."""
    start = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
    rows = db.query(
        func.date(Invoice.created_at).label("day"),
        func.coalesce(func.sum(Invoice.grand_total), 0).label("revenue"),
    ).filter(
        Invoice.payment_status == PaymentStatus.PAID, Invoice.created_at >= start
    ).group_by(func.date(Invoice.created_at)).all()
    return [{"date": str(row.day), "revenue": float(row.revenue)} for row in rows]
