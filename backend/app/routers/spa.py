from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.booking_billing import Booking
from app.models.spa import SpaService, Therapist, SpaBooking
from app.models.enums import BookingStatus, PaymentStatus, BookingType
from app.services.codes import generate_sub_booking_code, generate_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/spa", tags=["Spa & Massage"])


class SpaServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    service_price: float
    hourly_rate: Optional[float] = None


class SpaServiceOut(SpaServiceCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class TherapistOut(BaseModel):
    id: int
    name: str
    specialization: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class SpaBookingCreate(BaseModel):
    customer_id: int
    spa_service_id: int
    therapist_id: Optional[int] = None
    booking_date: datetime
    start_time: time
    duration_minutes: int = 60
    discount: float = 0
    tax: float = 0


class SpaBookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    spa_service_id: int
    therapist_id: Optional[int] = None
    booking_date: datetime
    start_time: time
    end_time: time
    duration_minutes: int
    amount: float
    discount: float
    tax: float
    total_amount: float
    payment_status: PaymentStatus
    booking_status: BookingStatus

    class Config:
        from_attributes = True


@router.get("/services", response_model=List[SpaServiceOut])
def list_spa_services(db: Session = Depends(get_db)):
    return db.query(SpaService).filter(SpaService.is_active == True).all()  # noqa: E712


@router.post("/services", response_model=SpaServiceOut)
def create_spa_service(payload: SpaServiceCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    service = SpaService(**payload.model_dump(), is_active=True)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/therapists", response_model=List[TherapistOut])
def list_therapists(db: Session = Depends(get_db)):
    return db.query(Therapist).filter(Therapist.is_active == True).all()  # noqa: E712


@router.post("/therapists", response_model=TherapistOut)
def create_therapist(name: str, specialization: Optional[str] = None, db: Session = Depends(get_db),
                      _=Depends(require_admin)):
    therapist = Therapist(name=name, specialization=specialization)
    db.add(therapist)
    db.commit()
    db.refresh(therapist)
    return therapist


def _therapist_has_conflict(db: Session, therapist_id: int, booking_date: datetime,
                             start_time: time, end_time: time) -> bool:
    """Prevent double spa booking for the same therapist (Section 51)."""
    if not therapist_id:
        return False
    same_day = db.query(SpaBooking).filter(
        SpaBooking.therapist_id == therapist_id,
        SpaBooking.booking_date == booking_date,
        SpaBooking.booking_status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        SpaBooking.start_time < end_time,
        SpaBooking.end_time > start_time,
    )
    return db.query(same_day.exists()).scalar()


@router.post("/bookings", response_model=SpaBookingOut)
def create_spa_booking(payload: SpaBookingCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    service = db.query(SpaService).filter(SpaService.id == payload.spa_service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Spa service not found")

    start_dt = datetime.combine(payload.booking_date.date(), payload.start_time)
    end_dt = start_dt + timedelta(minutes=payload.duration_minutes)
    end_time = end_dt.time()

    if _therapist_has_conflict(db, payload.therapist_id, payload.booking_date, payload.start_time, end_time):
        raise HTTPException(status_code=409, detail="This therapist is already booked for the selected time")

    if service.hourly_rate:
        amount = Decimal(str(service.hourly_rate)) * (Decimal(payload.duration_minutes) / 60)
    else:
        amount = Decimal(str(service.service_price))

    total_discount = apply_membership_discount(db, payload.customer_id, amount, payload.discount)
    total = calculate_grand_total(amount, payload.tax, total_discount)

    booking = SpaBooking(
        booking_code=generate_sub_booking_code(db, SpaBooking, SpaBooking.booking_code, "SP"),
        customer_id=payload.customer_id,
        spa_service_id=payload.spa_service_id,
        therapist_id=payload.therapist_id,
        booking_date=payload.booking_date,
        start_time=payload.start_time,
        end_time=end_time,
        duration_minutes=payload.duration_minutes,
        amount=amount,
        discount=total_discount,
        tax=payload.tax,
        total_amount=total,
        payment_status=PaymentStatus.PENDING,
        booking_status=BookingStatus.CONFIRMED,
    )
    db.add(booking)
    db.flush()

    central = Booking(
        booking_code=generate_booking_code(db),
        booking_type=BookingType.SPA_SESSION,
        reference_id=booking.id,
        customer_id=payload.customer_id,
        status=BookingStatus.CONFIRMED,
    )
    db.add(central)
    notify_customer(db, payload.customer_id, "Spa appointment confirmed",
                     f"Your spa booking {booking.booking_code} is confirmed for {payload.booking_date.date()}.")
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=List[SpaBookingOut])
def list_spa_bookings(customer_id: Optional[int] = None, db: Session = Depends(get_db),
                       _=Depends(get_current_user)):
    query = db.query(SpaBooking)
    if customer_id:
        query = query.filter(SpaBooking.customer_id == customer_id)
    return query.order_by(SpaBooking.id.desc()).all()
