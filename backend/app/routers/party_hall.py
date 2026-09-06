from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.booking_billing import Booking
from app.models.events import EventType, PartyHall, EventBooking
from app.models.enums import RateType, BookingStatus, PaymentStatus, BookingType
from app.services.codes import generate_sub_booking_code, generate_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/party-hall", tags=["Party Hall"])


class EventTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class HallCreate(BaseModel):
    name: str
    capacity: int
    location: Optional[str] = None
    facilities: Optional[str] = None
    hourly_rate: float = 0
    daily_rate: float = 0
    weekly_rate: float = 0


class HallOut(HallCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class EventBookingCreate(BaseModel):
    customer_id: int
    hall_id: int
    event_type_id: int
    event_date: datetime
    rate_type: RateType = RateType.DAILY
    duration: float
    additional_services_charge: float = 0
    discount: float = 0
    tax: float = 0


class EventBookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    hall_id: int
    event_type_id: int
    event_date: datetime
    rate_type: RateType
    duration: float
    hall_charges: float
    additional_services_charge: float
    discount: float
    tax: float
    total_amount: float
    payment_status: PaymentStatus
    booking_status: BookingStatus

    class Config:
        from_attributes = True


@router.get("/event-types", response_model=List[EventTypeOut])
def list_event_types(db: Session = Depends(get_db)):
    return db.query(EventType).all()


@router.post("/event-types", response_model=EventTypeOut)
def create_event_type(name: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    et = EventType(name=name)
    db.add(et)
    db.commit()
    db.refresh(et)
    return et


@router.get("/halls", response_model=List[HallOut])
def list_halls(db: Session = Depends(get_db)):
    return db.query(PartyHall).all()


@router.post("/halls", response_model=HallOut)
def create_hall(payload: HallCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    hall = PartyHall(**payload.model_dump(), status="available")
    db.add(hall)
    db.commit()
    db.refresh(hall)
    return hall


def _hall_has_conflict(db: Session, hall_id: int, event_date: datetime, exclude_id: Optional[int] = None) -> bool:
    """Prevent double event booking (Section 51)."""
    query = db.query(EventBooking).filter(
        EventBooking.hall_id == hall_id,
        EventBooking.event_date == event_date,
        EventBooking.booking_status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
    )
    if exclude_id:
        query = query.filter(EventBooking.id != exclude_id)
    return db.query(query.exists()).scalar()


@router.post("/bookings", response_model=EventBookingOut)
def create_event_booking(payload: EventBookingCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    hall = db.query(PartyHall).filter(PartyHall.id == payload.hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="Party hall not found")
    if _hall_has_conflict(db, payload.hall_id, payload.event_date):
        raise HTTPException(status_code=409, detail="This hall is already booked for the selected date")

    rate_map = {
        RateType.HOURLY: hall.hourly_rate,
        RateType.DAILY: hall.daily_rate,
        RateType.WEEKLY: hall.weekly_rate,
    }
    rate = Decimal(str(rate_map.get(payload.rate_type, hall.daily_rate) or 0))
    hall_charges = rate * Decimal(str(payload.duration))
    subtotal = hall_charges + Decimal(str(payload.additional_services_charge))
    total_discount = apply_membership_discount(db, payload.customer_id, subtotal, payload.discount)
    total = calculate_grand_total(subtotal, payload.tax, total_discount)

    booking = EventBooking(
        booking_code=generate_sub_booking_code(db, EventBooking, EventBooking.booking_code, "EV"),
        customer_id=payload.customer_id,
        hall_id=payload.hall_id,
        event_type_id=payload.event_type_id,
        event_date=payload.event_date,
        rate_type=payload.rate_type,
        duration=payload.duration,
        hall_charges=hall_charges,
        additional_services_charge=payload.additional_services_charge,
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
        booking_type=BookingType.EVENT,
        reference_id=booking.id,
        customer_id=payload.customer_id,
        status=BookingStatus.CONFIRMED,
    )
    db.add(central)
    notify_customer(db, payload.customer_id, "Event booking confirmed",
                     f"Your event booking {booking.booking_code} at {hall.name} is confirmed.")
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=List[EventBookingOut])
def list_event_bookings(customer_id: Optional[int] = None, db: Session = Depends(get_db),
                         _=Depends(get_current_user)):
    query = db.query(EventBooking)
    if customer_id:
        query = query.filter(EventBooking.customer_id == customer_id)
    return query.order_by(EventBooking.id.desc()).all()


@router.post("/bookings/{booking_id}/cancel", response_model=EventBookingOut)
def cancel_event_booking(booking_id: int, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    booking = db.query(EventBooking).filter(EventBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.booking_status = BookingStatus.CANCELLED
    notify_customer(db, booking.customer_id, "Event booking cancelled",
                     f"Your event booking {booking.booking_code} has been cancelled.")
    db.commit()
    db.refresh(booking)
    return booking
