from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.booking_billing import Booking
from app.models.pool import PoolPackagePrice, Trainer, PoolBooking
from app.models.enums import PoolCustomerType, PoolPackageType, BookingStatus, PaymentStatus, BookingType
from app.services.codes import generate_sub_booking_code, generate_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/pool", tags=["Swimming Pool"])


class PriceSet(BaseModel):
    customer_type: PoolCustomerType
    package_type: PoolPackageType
    price: float


class PriceOut(PriceSet):
    id: int

    class Config:
        from_attributes = True


class TrainerOut(BaseModel):
    id: int
    name: str
    specialization: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class PoolBookingCreate(BaseModel):
    customer_id: int
    customer_type: PoolCustomerType
    package_type: PoolPackageType
    trainer_id: Optional[int] = None
    booking_date: datetime
    discount: float = 0
    tax: float = 0


class PoolBookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    customer_type: PoolCustomerType
    package_type: PoolPackageType
    trainer_id: Optional[int] = None
    booking_date: datetime
    package_amount: float
    discount: float
    tax: float
    total_amount: float
    payment_status: PaymentStatus
    booking_status: BookingStatus

    class Config:
        from_attributes = True


@router.get("/prices", response_model=List[PriceOut])
def list_prices(db: Session = Depends(get_db)):
    return db.query(PoolPackagePrice).all()


@router.put("/prices", response_model=PriceOut)
def set_price(payload: PriceSet, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Admin can configure the price for each customer-type / package-type combination (Section 26)."""
    existing = db.query(PoolPackagePrice).filter(
        PoolPackagePrice.customer_type == payload.customer_type,
        PoolPackagePrice.package_type == payload.package_type,
    ).first()
    if existing:
        existing.price = payload.price
        db.commit()
        db.refresh(existing)
        return existing
    price = PoolPackagePrice(**payload.model_dump())
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


@router.get("/trainers", response_model=List[TrainerOut])
def list_trainers(db: Session = Depends(get_db)):
    return db.query(Trainer).filter(Trainer.is_active == True).all()  # noqa: E712


@router.post("/trainers", response_model=TrainerOut)
def create_trainer(name: str, specialization: Optional[str] = None, db: Session = Depends(get_db),
                    _=Depends(require_admin)):
    trainer = Trainer(name=name, specialization=specialization)
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer


@router.post("/bookings", response_model=PoolBookingOut)
def create_pool_booking(payload: PoolBookingCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    price_row = db.query(PoolPackagePrice).filter(
        PoolPackagePrice.customer_type == payload.customer_type,
        PoolPackagePrice.package_type == payload.package_type,
    ).first()
    if not price_row:
        raise HTTPException(status_code=400, detail="No price configured for this customer/package combination")
    if payload.package_type == PoolPackageType.TRAINER and not payload.trainer_id:
        raise HTTPException(status_code=400, detail="A trainer must be selected for the trainer package")

    total_discount = apply_membership_discount(db, payload.customer_id, price_row.price, payload.discount)
    total = calculate_grand_total(price_row.price, payload.tax, total_discount)

    booking = PoolBooking(
        booking_code=generate_sub_booking_code(db, PoolBooking, PoolBooking.booking_code, "PL"),
        customer_id=payload.customer_id,
        customer_type=payload.customer_type,
        package_type=payload.package_type,
        trainer_id=payload.trainer_id,
        booking_date=payload.booking_date,
        package_amount=price_row.price,
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
        booking_type=BookingType.SWIMMING_POOL,
        reference_id=booking.id,
        customer_id=payload.customer_id,
        status=BookingStatus.CONFIRMED,
    )
    db.add(central)
    notify_customer(db, payload.customer_id, "Pool booking confirmed",
                     f"Your swimming pool booking {booking.booking_code} is confirmed.")
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=List[PoolBookingOut])
def list_pool_bookings(customer_id: Optional[int] = None, db: Session = Depends(get_db),
                        _=Depends(get_current_user)):
    query = db.query(PoolBooking)
    if customer_id:
        query = query.filter(PoolBooking.customer_id == customer_id)
    return query.order_by(PoolBooking.id.desc()).all()
