from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_management, require_room_staff, require_staff_any
from app.models.accommodation import RoomType, Room, RoomBooking
from app.models.booking_billing import Booking
from app.models.core import User
from app.models.enums import (
    RoomStatus, RoomCustomerCategory, RateType, BookingStatus, PaymentStatus, BookingType,
)
from app.services.codes import generate_sub_booking_code, generate_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/rooms", tags=["Accommodation"])


# ---------- Schemas ----------

class RoomTypeCreate(BaseModel):
    name: str
    customer_category: RoomCustomerCategory
    description: Optional[str] = None
    hourly_rate: float = 0
    daily_rate: float = 0
    weekly_rate: float = 0
    monthly_rate: float = 0
    max_adults: int = 2
    max_children: int = 1


class RoomTypeOut(RoomTypeCreate):
    id: int

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    room_number: str
    room_type_id: int
    floor: Optional[str] = None


class RoomOut(BaseModel):
    id: int
    room_number: str
    room_type_id: int
    floor: Optional[str] = None
    status: RoomStatus

    class Config:
        from_attributes = True


class RoomBookingCreate(BaseModel):
    customer_id: int
    room_id: int
    check_in_date: datetime
    check_in_time: Optional[time] = None
    check_out_date: datetime
    check_out_time: Optional[time] = None
    adults: int = 1
    children: int = 0
    rate_type: RateType = RateType.DAILY
    discount: float = 0
    tax: float = 0


class RoomBookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    adults: int
    children: int
    rate_type: RateType
    room_rate: float
    duration: float
    discount: float
    tax: float
    total_amount: float
    payment_status: PaymentStatus
    booking_status: BookingStatus

    class Config:
        from_attributes = True


# ---------- Room Types ----------

@router.get("/types", response_model=List[RoomTypeOut])
def list_room_types(db: Session = Depends(get_db)):
    return db.query(RoomType).all()


@router.post("/types", response_model=RoomTypeOut)
def create_room_type(payload: RoomTypeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    room_type = RoomType(**payload.model_dump())
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


# ---------- Rooms ----------

@router.get("", response_model=List[RoomOut])
def list_rooms(status_filter: Optional[RoomStatus] = None, room_type_id: Optional[int] = None,
               db: Session = Depends(get_db)):
    query = db.query(Room)
    if status_filter:
        query = query.filter(Room.status == status_filter)
    if room_type_id:
        query = query.filter(Room.room_type_id == room_type_id)
    return query.all()


@router.post("", response_model=RoomOut)
def create_room(payload: RoomCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Room).filter(Room.room_number == payload.room_number).first():
        raise HTTPException(status_code=400, detail="Room number already exists")
    room = Room(**payload.model_dump(), status=RoomStatus.AVAILABLE)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.put("/{room_id}/status", response_model=RoomOut)
def update_room_status(room_id: int, new_status: RoomStatus, db: Session = Depends(get_db),
                        _=Depends(require_room_staff)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.status = new_status
    db.commit()
    db.refresh(room)
    return room


# ---------- Availability ----------

def _room_has_conflict(db: Session, room_id: int, check_in: datetime, check_out: datetime,
                        exclude_booking_id: Optional[int] = None) -> bool:
    """Prevent double room booking (Section 51 testing requirement)."""
    query = db.query(RoomBooking).filter(
        RoomBooking.room_id == room_id,
        RoomBooking.booking_status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
        RoomBooking.check_in_date < check_out,
        RoomBooking.check_out_date > check_in,
    )
    if exclude_booking_id:
        query = query.filter(RoomBooking.id != exclude_booking_id)
    return db.query(query.exists()).scalar()


@router.get("/availability")
def check_room_availability(room_id: int, check_in_date: datetime, check_out_date: datetime,
                             db: Session = Depends(get_db)):
    conflict = _room_has_conflict(db, room_id, check_in_date, check_out_date)
    return {"room_id": room_id, "available": not conflict}


def _calculate_duration_and_rate(room_type: RoomType, rate_type: RateType, check_in: datetime, check_out: datetime):
    delta = check_out - check_in
    if rate_type == RateType.HOURLY:
        duration = max(Decimal(str(delta.total_seconds() / 3600)), Decimal("1"))
        rate = Decimal(str(room_type.hourly_rate))
    elif rate_type == RateType.WEEKLY:
        duration = max(Decimal(str(delta.days / 7)).quantize(Decimal("1")), Decimal("1"))
        rate = Decimal(str(room_type.weekly_rate))
    elif rate_type == RateType.MONTHLY:
        duration = max(Decimal(str(delta.days / 30)).quantize(Decimal("1")), Decimal("1"))
        rate = Decimal(str(room_type.monthly_rate))
    else:  # DAILY
        duration = max(Decimal(delta.days if delta.days > 0 else 1), Decimal("1"))
        rate = Decimal(str(room_type.daily_rate))
    return duration, rate


# ---------- Room Bookings ----------

@router.post("/bookings", response_model=RoomBookingOut)
def create_room_booking(payload: RoomBookingCreate, db: Session = Depends(get_db),
                         _=Depends(require_staff_any)):
    room = db.query(Room).filter(Room.id == payload.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if payload.check_out_date <= payload.check_in_date:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")
    if _room_has_conflict(db, payload.room_id, payload.check_in_date, payload.check_out_date):
        raise HTTPException(status_code=409, detail="Room is already booked for the selected dates")

    room_type = room.room_type
    if payload.adults > room_type.max_adults or payload.children > room_type.max_children:
        raise HTTPException(status_code=400, detail="Guest count exceeds this room type's capacity")

    duration, rate = _calculate_duration_and_rate(room_type, payload.rate_type, payload.check_in_date,
                                                   payload.check_out_date)
    subtotal = rate * duration
    # Membership Benefits (Section 6) automatically discount room bookings on top of any
    # manual discount a staff member enters.
    total_discount = apply_membership_discount(db, payload.customer_id, subtotal, payload.discount)
    total = calculate_grand_total(subtotal, payload.tax, total_discount)

    booking = RoomBooking(
        booking_code=generate_sub_booking_code(db, RoomBooking, RoomBooking.booking_code, "RM"),
        customer_id=payload.customer_id,
        room_id=payload.room_id,
        check_in_date=payload.check_in_date,
        check_in_time=payload.check_in_time,
        check_out_date=payload.check_out_date,
        check_out_time=payload.check_out_time,
        adults=payload.adults,
        children=payload.children,
        rate_type=payload.rate_type,
        room_rate=rate,
        duration=duration,
        discount=total_discount,
        tax=payload.tax,
        total_amount=total,
        payment_status=PaymentStatus.PENDING,
        booking_status=BookingStatus.CONFIRMED,
    )
    db.add(booking)
    room.status = RoomStatus.NOT_AVAILABLE
    db.flush()

    central = Booking(
        booking_code=generate_booking_code(db),
        booking_type=BookingType.ROOM,
        reference_id=booking.id,
        customer_id=payload.customer_id,
        status=BookingStatus.CONFIRMED,
    )
    db.add(central)
    notify_customer(
        db, payload.customer_id, "Room booking confirmed",
        f"Your booking {booking.booking_code} for room {room.room_number} is confirmed.",
    )
    db.commit()
    db.refresh(booking)
    return booking


class RoomBookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_in_time: Optional[time] = None
    check_out_date: Optional[datetime] = None
    check_out_time: Optional[time] = None
    adults: Optional[int] = None
    children: Optional[int] = None


@router.put("/bookings/{booking_id}", response_model=RoomBookingOut)
def modify_room_booking(booking_id: int, payload: RoomBookingUpdate, db: Session = Depends(get_db),
                         _=Depends(require_staff_any)):
    """Modify Booking (Section 50: Manage Your Booking customer options) — re-validates
    availability and recalculates the total when dates change."""
    booking = db.query(RoomBooking).filter(RoomBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
        raise HTTPException(status_code=400, detail="Only pending or confirmed bookings can be modified")

    new_check_in = payload.check_in_date or booking.check_in_date
    new_check_out = payload.check_out_date or booking.check_out_date
    if new_check_out <= new_check_in:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    dates_changed = new_check_in != booking.check_in_date or new_check_out != booking.check_out_date
    if dates_changed and _room_has_conflict(db, booking.room_id, new_check_in, new_check_out, exclude_booking_id=booking.id):
        raise HTTPException(status_code=409, detail="Room is already booked for the newly selected dates")

    room_type = booking.room.room_type
    new_adults = payload.adults if payload.adults is not None else booking.adults
    new_children = payload.children if payload.children is not None else booking.children
    if new_adults > room_type.max_adults or new_children > room_type.max_children:
        raise HTTPException(status_code=400, detail="Guest count exceeds this room type's capacity")

    if dates_changed:
        # Keep the discount amount already fixed at booking time; only the rate/duration/total
        # need recalculating for the new dates.
        duration, rate = _calculate_duration_and_rate(room_type, booking.rate_type, new_check_in, new_check_out)
        subtotal = rate * duration
        booking.room_rate = rate
        booking.duration = duration
        booking.total_amount = calculate_grand_total(subtotal, booking.tax, booking.discount)

    booking.check_in_date = new_check_in
    booking.check_in_time = payload.check_in_time if payload.check_in_time is not None else booking.check_in_time
    booking.check_out_date = new_check_out
    booking.check_out_time = payload.check_out_time if payload.check_out_time is not None else booking.check_out_time
    booking.adults = new_adults
    booking.children = new_children

    notify_customer(db, booking.customer_id, "Booking updated",
                     f"Your booking {booking.booking_code} has been updated.")
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=List[RoomBookingOut])
def list_room_bookings(customer_id: Optional[int] = None, status_filter: Optional[BookingStatus] = None,
                        db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(RoomBooking)
    if customer_id:
        query = query.filter(RoomBooking.customer_id == customer_id)
    if status_filter:
        query = query.filter(RoomBooking.booking_status == status_filter)
    return query.order_by(RoomBooking.id.desc()).all()


@router.get("/bookings/{booking_id}", response_model=RoomBookingOut)
def get_room_booking(booking_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    booking = db.query(RoomBooking).filter(RoomBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/bookings/{booking_id}/check-in", response_model=RoomBookingOut)
def check_in(booking_id: int, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    booking = db.query(RoomBooking).filter(RoomBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status != BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Only confirmed bookings can be checked in")
    booking.booking_status = BookingStatus.CHECKED_IN
    notify_customer(db, booking.customer_id, "Checked in",
                     f"You've been checked in to room {booking.room.room_number}. Enjoy your stay!")
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/bookings/{booking_id}/check-out", response_model=RoomBookingOut)
def check_out(booking_id: int, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    booking = db.query(RoomBooking).filter(RoomBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status != BookingStatus.CHECKED_IN:
        raise HTTPException(status_code=400, detail="Only checked-in bookings can be checked out")
    booking.booking_status = BookingStatus.CHECKED_OUT
    booking.room.status = RoomStatus.UNDER_CLEANING
    notify_customer(db, booking.customer_id, "Checked out",
                     f"You've been checked out of room {booking.room.room_number}. Thank you for staying with us!")
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/bookings/{booking_id}/cancel", response_model=RoomBookingOut)
def cancel_room_booking(booking_id: int, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    booking = db.query(RoomBooking).filter(RoomBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.booking_status in (BookingStatus.CHECKED_OUT, BookingStatus.COMPLETED):
        raise HTTPException(status_code=400, detail="This booking can no longer be cancelled")
    booking.booking_status = BookingStatus.CANCELLED
    if booking.room.status == RoomStatus.NOT_AVAILABLE:
        booking.room.status = RoomStatus.AVAILABLE
    notify_customer(db, booking.customer_id, "Booking cancelled",
                     f"Your booking {booking.booking_code} has been cancelled.")
    db.commit()
    db.refresh(booking)
    return booking
