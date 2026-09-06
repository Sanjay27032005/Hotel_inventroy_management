from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_reports_access
from app.models.core import Employee, Department, User, AuditLog
from app.models.accommodation import RoomBooking, Room, RoomType
from app.models.restaurant import FoodOrder, FoodOrderItem, FoodItem, FoodCategory, RestaurantBooking
from app.models.events import EventBooking
from app.models.spa import SpaBooking, SpaService, Therapist
from app.models.pool import PoolBooking, Trainer
from app.models.laundry import LaundryOrder, LaundryOrderItem
from app.models.booking_billing import Invoice, Payment
from app.models.enums import PaymentStatus, BookingStatus, LaundryStatus, PoolPackageType, UserRole

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _date_range(start: Optional[date], end: Optional[date]):
    start_dt = datetime.combine(start or (date.today() - timedelta(days=30)), datetime.min.time())
    end_dt = datetime.combine((end or date.today()) + timedelta(days=1), datetime.min.time())
    return start_dt, end_dt


# ---------- Accommodation Reports ----------

@router.get("/accommodation/bookings")
def room_booking_report(start: Optional[date] = None, end: Optional[date] = None,
                         db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    return db.query(RoomBooking).filter(
        RoomBooking.created_at >= start_dt, RoomBooking.created_at < end_dt
    ).all()


@router.get("/accommodation/occupancy")
def room_occupancy_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    total = db.query(func.count(Room.id)).scalar() or 0
    by_status = db.query(Room.status, func.count(Room.id)).group_by(Room.status).all()
    return {
        "total_rooms": total,
        "by_status": {status.value: count for status, count in by_status},
    }


@router.get("/accommodation/check-in")
def check_in_report(target_date: Optional[date] = None, db: Session = Depends(get_db),
                     _=Depends(require_reports_access)):
    """Check-In Report (Section 67): bookings checked in on the given day, defaulting to today."""
    day = target_date or date.today()
    start_dt = datetime.combine(day, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    return db.query(RoomBooking).filter(
        RoomBooking.booking_status.in_([BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT]),
        RoomBooking.check_in_date >= start_dt, RoomBooking.check_in_date < end_dt,
    ).all()


@router.get("/accommodation/check-out")
def check_out_report(target_date: Optional[date] = None, db: Session = Depends(get_db),
                      _=Depends(require_reports_access)):
    """Check-Out Report (Section 67): bookings checked out on the given day, defaulting to today."""
    day = target_date or date.today()
    start_dt = datetime.combine(day, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    return db.query(RoomBooking).filter(
        RoomBooking.booking_status == BookingStatus.CHECKED_OUT,
        RoomBooking.check_out_date >= start_dt, RoomBooking.check_out_date < end_dt,
    ).all()


@router.get("/accommodation/revenue")
def accommodation_revenue_report(start: Optional[date] = None, end: Optional[date] = None,
                                  db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    total = db.query(func.coalesce(func.sum(RoomBooking.total_amount), 0)).filter(
        RoomBooking.created_at >= start_dt, RoomBooking.created_at < end_dt
    ).scalar()
    return {"total_room_revenue": float(total or 0)}


# ---------- Restaurant Reports ----------

@router.get("/restaurant/table-bookings")
def table_booking_report(start: Optional[date] = None, end: Optional[date] = None,
                          db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    return db.query(RestaurantBooking).filter(
        RestaurantBooking.created_at >= start_dt, RestaurantBooking.created_at < end_dt
    ).all()


@router.get("/restaurant/food-sales")
def food_sales_report(start: Optional[date] = None, end: Optional[date] = None,
                       db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    rows = db.query(
        FoodItem.name, func.sum(FoodOrderItem.quantity).label("qty"), func.sum(FoodOrderItem.amount).label("amt")
    ).join(FoodOrderItem, FoodOrderItem.food_item_id == FoodItem.id).join(
        FoodOrder, FoodOrder.id == FoodOrderItem.order_id
    ).filter(FoodOrder.created_at >= start_dt, FoodOrder.created_at < end_dt).group_by(FoodItem.name).all()
    return [{"food_item": name, "quantity_sold": int(qty), "revenue": float(amt)} for name, qty, amt in rows]


@router.get("/restaurant/daily-revenue")
def restaurant_daily_revenue(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    rows = db.query(
        func.date(FoodOrder.created_at).label("day"), func.coalesce(func.sum(FoodOrder.total_amount), 0)
    ).group_by(func.date(FoodOrder.created_at)).all()
    return [{"date": str(day), "revenue": float(amt)} for day, amt in rows]


@router.get("/restaurant/category-wise-sales")
def restaurant_category_wise_sales(start: Optional[date] = None, end: Optional[date] = None,
                                    db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    rows = db.query(
        FoodCategory.name, func.sum(FoodOrderItem.quantity), func.sum(FoodOrderItem.amount)
    ).join(FoodItem, FoodItem.category_id == FoodCategory.id) \
     .join(FoodOrderItem, FoodOrderItem.food_item_id == FoodItem.id) \
     .join(FoodOrder, FoodOrder.id == FoodOrderItem.order_id) \
     .filter(FoodOrder.created_at >= start_dt, FoodOrder.created_at < end_dt) \
     .group_by(FoodCategory.name).all()
    return [{"category": name, "quantity_sold": int(qty), "revenue": float(rev)} for name, qty, rev in rows]


# ---------- Event Reports ----------

@router.get("/events/bookings")
def event_bookings_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    return db.query(EventBooking).order_by(EventBooking.event_date.desc()).all()


@router.get("/events/upcoming")
def upcoming_events_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    return db.query(EventBooking).filter(
        EventBooking.event_date >= datetime.utcnow(), EventBooking.booking_status == BookingStatus.CONFIRMED
    ).order_by(EventBooking.event_date).all()


@router.get("/events/revenue")
def event_revenue_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    total = db.query(func.coalesce(func.sum(EventBooking.total_amount), 0)).scalar()
    return {"total_event_revenue": float(total or 0)}


# ---------- Spa Reports ----------

@router.get("/spa/bookings")
def spa_bookings_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    return db.query(SpaBooking).order_by(SpaBooking.booking_date.desc()).all()


@router.get("/spa/therapist-sessions")
def therapist_sessions_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    rows = db.query(Therapist.name, func.count(SpaBooking.id), func.coalesce(func.sum(SpaBooking.total_amount), 0)) \
        .join(SpaBooking, SpaBooking.therapist_id == Therapist.id) \
        .group_by(Therapist.name).all()
    return [{"therapist": name, "sessions": int(count), "revenue": float(rev)} for name, count, rev in rows]


@router.get("/spa/service-report")
def spa_service_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Massage Service Report (Section 67): bookings and revenue per spa service."""
    rows = db.query(
        SpaService.name, func.count(SpaBooking.id), func.coalesce(func.sum(SpaBooking.total_amount), 0)
    ).join(SpaBooking, SpaBooking.spa_service_id == SpaService.id) \
     .group_by(SpaService.name).all()
    return [{"service": name, "sessions": int(count), "revenue": float(rev)} for name, count, rev in rows]


@router.get("/spa/revenue")
def spa_revenue_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    total = db.query(func.coalesce(func.sum(SpaBooking.total_amount), 0)).scalar()
    return {"total_spa_revenue": float(total or 0)}


# ---------- Pool Reports ----------

@router.get("/pool/package-sales")
def pool_package_sales_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    rows = db.query(
        PoolBooking.package_type, PoolBooking.customer_type,
        func.count(PoolBooking.id), func.coalesce(func.sum(PoolBooking.total_amount), 0)
    ).group_by(PoolBooking.package_type, PoolBooking.customer_type).all()
    return [
        {"package_type": pt.value, "customer_type": ct.value, "bookings": int(count), "revenue": float(rev)}
        for pt, ct, count, rev in rows
    ]


@router.get("/pool/customer-type-report")
def pool_customer_type_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Child/Adult/Couple Report (Section 67): bookings and revenue by customer type, across all packages."""
    rows = db.query(
        PoolBooking.customer_type, func.count(PoolBooking.id), func.coalesce(func.sum(PoolBooking.total_amount), 0)
    ).group_by(PoolBooking.customer_type).all()
    return [{"customer_type": ct.value, "bookings": int(count), "revenue": float(rev)} for ct, count, rev in rows]


@router.get("/pool/trainer-package-report")
def pool_trainer_package_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Trainer Package Report (Section 67): trainer-led bookings grouped by trainer."""
    rows = db.query(
        Trainer.name, func.count(PoolBooking.id), func.coalesce(func.sum(PoolBooking.total_amount), 0)
    ).join(PoolBooking, PoolBooking.trainer_id == Trainer.id) \
     .filter(PoolBooking.package_type == PoolPackageType.TRAINER) \
     .group_by(Trainer.name).all()
    return [{"trainer": name, "bookings": int(count), "revenue": float(rev)} for name, count, rev in rows]


# ---------- Laundry Reports ----------

@router.get("/laundry/orders")
def laundry_orders_report(status_filter: Optional[LaundryStatus] = None, db: Session = Depends(get_db),
                           _=Depends(require_reports_access)):
    query = db.query(LaundryOrder)
    if status_filter:
        query = query.filter(LaundryOrder.status == status_filter)
    return query.order_by(LaundryOrder.created_at.desc()).all()


@router.get("/laundry/cloth-wise-sales")
def laundry_cloth_wise_sales(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    rows = db.query(
        LaundryOrderItem.cloth_type, func.sum(LaundryOrderItem.quantity), func.sum(LaundryOrderItem.amount)
    ).group_by(LaundryOrderItem.cloth_type).all()
    return [{"cloth_type": ct, "quantity": int(q), "revenue": float(r)} for ct, q, r in rows]


@router.get("/laundry/quantity-wise-sales")
def laundry_quantity_wise_sales(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Quantity-wise Sales (Section 67): sales broken down by pricing method (cloth-based vs
    quantity-based), since that's the axis the requirement document distinguishes billing on."""
    rows = db.query(
        LaundryOrder.pricing_method, func.count(LaundryOrder.id), func.coalesce(func.sum(LaundryOrder.total_amount), 0)
    ).group_by(LaundryOrder.pricing_method).all()
    return [{"pricing_method": pm.value, "orders": int(count), "revenue": float(rev)} for pm, count, rev in rows]


@router.get("/laundry/revenue")
def laundry_revenue_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    total = db.query(func.coalesce(func.sum(LaundryOrder.total_amount), 0)).scalar()
    return {"total_laundry_revenue": float(total or 0)}


@router.get("/laundry/pending")
def pending_laundry_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    return db.query(LaundryOrder).filter(
        LaundryOrder.status.notin_([LaundryStatus.DELIVERED, LaundryStatus.CANCELLED])
    ).all()


# ---------- Financial Reports ----------

@router.get("/financial/summary")
def financial_summary(start: Optional[date] = None, end: Optional[date] = None,
                       db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    by_service = db.query(
        Invoice.service_type, func.coalesce(func.sum(Invoice.grand_total), 0)
    ).filter(
        Invoice.payment_status == PaymentStatus.PAID, Invoice.created_at >= start_dt, Invoice.created_at < end_dt
    ).group_by(Invoice.service_type).all()

    pending_total = db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
        Invoice.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIALLY_PAID])
    ).scalar()

    total_discounts = db.query(func.coalesce(func.sum(Invoice.discount), 0)).filter(
        Invoice.created_at >= start_dt, Invoice.created_at < end_dt
    ).scalar()

    return {
        "service_wise_revenue": {st.value: float(rev) for st, rev in by_service},
        "pending_payments_total": float(pending_total or 0),
        "total_discounts_given": float(total_discounts or 0),
    }


@router.get("/financial/payments")
def payment_report(start: Optional[date] = None, end: Optional[date] = None,
                    db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt, end_dt = _date_range(start, end)
    return db.query(Payment).filter(Payment.paid_at >= start_dt, Payment.paid_at < end_dt).all()


@router.get("/financial/daily-revenue")
def financial_daily_revenue(days: int = 30, db: Session = Depends(get_db), _=Depends(require_reports_access)):
    start_dt = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
    rows = db.query(
        func.date(Invoice.created_at).label("day"), func.coalesce(func.sum(Invoice.grand_total), 0)
    ).filter(Invoice.payment_status == PaymentStatus.PAID, Invoice.created_at >= start_dt) \
     .group_by(func.date(Invoice.created_at)).all()
    return [{"date": str(day), "revenue": float(rev)} for day, rev in rows]


@router.get("/financial/monthly-revenue")
def financial_monthly_revenue(months: int = 12, db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Grouped in Python rather than SQL (func.strftime/date_trunc differ across SQLite/Postgres),
    so this works identically on either database."""
    start_dt = datetime.combine(date.today() - timedelta(days=months * 31), datetime.min.time())
    rows = db.query(Invoice.created_at, Invoice.grand_total).filter(
        Invoice.payment_status == PaymentStatus.PAID, Invoice.created_at >= start_dt
    ).all()
    totals = {}
    for created_at, grand_total in rows:
        key = created_at.strftime("%Y-%m")
        totals[key] = totals.get(key, 0) + float(grand_total)
    return [{"month": month, "revenue": revenue} for month, revenue in sorted(totals.items())]


@router.get("/financial/invoices")
def invoice_report(start: Optional[date] = None, end: Optional[date] = None,
                    service_type: Optional[str] = None, payment_status: Optional[PaymentStatus] = None,
                    db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Invoice Report (Section 67): full invoice list with filters."""
    start_dt, end_dt = _date_range(start, end)
    query = db.query(Invoice).filter(Invoice.created_at >= start_dt, Invoice.created_at < end_dt)
    if service_type:
        query = query.filter(Invoice.service_type == service_type)
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    return query.order_by(Invoice.created_at.desc()).all()


@router.get("/financial/discounts")
def discount_report(start: Optional[date] = None, end: Optional[date] = None,
                     db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Discount Report (Section 67): discount totals broken down by service, plus the
    most-discounted invoices in the period."""
    start_dt, end_dt = _date_range(start, end)
    by_service = db.query(
        Invoice.service_type, func.coalesce(func.sum(Invoice.discount), 0), func.count(Invoice.id)
    ).filter(Invoice.created_at >= start_dt, Invoice.created_at < end_dt, Invoice.discount > 0) \
     .group_by(Invoice.service_type).all()
    top_discounted = db.query(Invoice).filter(
        Invoice.created_at >= start_dt, Invoice.created_at < end_dt, Invoice.discount > 0
    ).order_by(Invoice.discount.desc()).limit(10).all()
    return {
        "by_service": [
            {"service_type": st.value, "total_discount": float(disc), "invoice_count": int(count)}
            for st, disc, count in by_service
        ],
        "top_discounted_invoices": [
            {"invoice_number": inv.invoice_number, "discount": float(inv.discount), "grand_total": float(inv.grand_total)}
            for inv in top_discounted
        ],
    }


# ---------- Employee Reports ----------

@router.get("/employees/list")
def employee_list_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    return db.query(Employee).all()


@router.get("/employees/department-wise")
def department_wise_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    rows = db.query(Department.name, func.count(Employee.id)).join(
        Employee, Employee.department_id == Department.id
    ).group_by(Department.name).all()
    return [{"department": name, "employee_count": int(count)} for name, count in rows]


@router.get("/employees/activity")
def employee_activity_report(limit: int = 100, db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """Employee Activity (Section 67): recent audit log entries for staff accounts."""
    rows = db.query(AuditLog, User, Employee).join(User, AuditLog.user_id == User.id) \
        .outerjoin(Employee, User.employee_id == Employee.id) \
        .filter(User.role != UserRole.CUSTOMER) \
        .order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "employee": f"{emp.first_name} {emp.last_name}" if emp else user.username,
            "action": log.action,
            "details": log.details,
            "at": log.created_at,
        }
        for log, user, emp in rows
    ]


@router.get("/employees/login-activity")
def employee_login_activity_report(db: Session = Depends(get_db), _=Depends(require_reports_access)):
    """User Login Activity (Section 67): each staff account's last login time."""
    rows = db.query(Employee, User).join(User, User.employee_id == Employee.id).all()
    return [
        {
            "employee": f"{emp.first_name} {emp.last_name}",
            "username": user.username,
            "role": user.role.value,
            "last_login": user.last_login,
        }
        for emp, user in rows
    ]
