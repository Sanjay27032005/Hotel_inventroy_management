from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_staff_any
from app.models.booking_billing import Booking, StayRequest, Invoice
from app.models.customer import Customer
from app.models.enums import BookingType, BookingStatus, EnquiryStatus, InvoiceServiceType
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

# Maps the central booking registry's BookingType to the InvoiceServiceType used by
# billing, and to the underlying model + its status field names — needed to show
# "view invoice", "view payment status" from Manage Your Booking (Section 50).
_BOOKING_TYPE_INFO = {}


def _load_booking_type_info():
    if _BOOKING_TYPE_INFO:
        return _BOOKING_TYPE_INFO
    from app.models.accommodation import RoomBooking
    from app.models.restaurant import RestaurantBooking, FoodOrder
    from app.models.events import EventBooking
    from app.models.pool import PoolBooking
    from app.models.spa import SpaBooking
    from app.models.club import ClubOrder
    from app.models.laundry import LaundryOrder

    _BOOKING_TYPE_INFO.update({
        BookingType.ROOM: (RoomBooking, InvoiceServiceType.ACCOMMODATION, "booking_status"),
        BookingType.DINING_TABLE: (RestaurantBooking, None, "status"),
        BookingType.EVENT: (EventBooking, InvoiceServiceType.PARTY_HALL, "booking_status"),
        BookingType.SWIMMING_POOL: (PoolBooking, InvoiceServiceType.SWIMMING_POOL, "booking_status"),
        BookingType.SPA_SESSION: (SpaBooking, InvoiceServiceType.SPA, "booking_status"),
        BookingType.CLUB: (ClubOrder, InvoiceServiceType.CLUB_BAR, "payment_status"),
        BookingType.LAUNDRY: (LaundryOrder, InvoiceServiceType.LAUNDRY, "status"),
    })
    return _BOOKING_TYPE_INFO


class BookingOut(BaseModel):
    id: int
    booking_code: str
    booking_type: BookingType
    reference_id: int
    customer_id: int
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class StayRequestCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    requirement_text: Optional[str] = None


class StayRequestOut(StayRequestCreate):
    id: int
    status: EnquiryStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Manage Your Booking (Section 50: public lookup by booking ID or email/phone) ----------

@router.get("/lookup", response_model=List[BookingOut])
def lookup_booking(booking_code: Optional[str] = None, email: Optional[str] = None,
                    phone: Optional[str] = None, db: Session = Depends(get_db)):
    if not booking_code and not (email or phone):
        raise HTTPException(status_code=400, detail="Provide a booking ID, or an email/phone to search by")

    query = db.query(Booking)
    if booking_code:
        query = query.filter(Booking.booking_code == booking_code)
    else:
        customer_query = db.query(Customer.id)
        if email:
            customer_query = customer_query.filter(Customer.email == email)
        if phone:
            customer_query = customer_query.filter(Customer.phone == phone)
        customer_ids = [row[0] for row in customer_query.all()]
        if not customer_ids:
            return []
        query = query.filter(Booking.customer_id.in_(customer_ids))

    return query.order_by(Booking.id.desc()).all()


@router.get("/{booking_id}/detail")
def booking_detail(booking_id: int, db: Session = Depends(get_db)):
    """Manage Your Booking (Section 50): view booking details, view invoice, and view
    payment status, all from one lookup."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    info = _load_booking_type_info().get(booking.booking_type)
    sub_booking = None
    invoice_summary = None
    if info:
        model, invoice_service_type, status_field = info
        record = db.query(model).filter(model.id == booking.reference_id).first()
        if record:
            sub_booking = {
                "id": record.id,
                "code": getattr(record, "booking_code", None) or getattr(record, "order_code", None),
                "status": getattr(record, status_field).value if getattr(record, status_field) else None,
                "payment_status": getattr(record, "payment_status", None).value if getattr(record, "payment_status", None) else None,
                "total_amount": float(getattr(record, "total_amount", 0) or 0),
            }
        if invoice_service_type:
            invoice = db.query(Invoice).filter(
                Invoice.service_type == invoice_service_type, Invoice.reference_id == booking.reference_id
            ).first()
            if invoice:
                invoice_summary = {
                    "id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "grand_total": float(invoice.grand_total),
                    "payment_status": invoice.payment_status.value,
                    "pdf_url": f"/api/billing/invoices/{invoice.id}/pdf",
                }

    return {
        "booking_code": booking.booking_code,
        "booking_type": booking.booking_type.value,
        "status": booking.status.value,
        "created_at": booking.created_at,
        "sub_booking": sub_booking,
        "invoice": invoice_summary,
    }


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def request_cancellation(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.CANCELLED

    # Keep the underlying service booking in sync, not just the central registry row —
    # otherwise the room/table/hall never gets released and staff-side screens disagree
    # with what the customer sees here.
    info = _load_booking_type_info().get(booking.booking_type)
    if info:
        model, _invoice_service_type, status_field = info
        record = db.query(model).filter(model.id == booking.reference_id).first()
        if record:
            current_status = getattr(record, status_field, None)
            enum_type = type(current_status) if current_status is not None else None
            # Only overwrite the sub-booking's own status if that enum actually has a
            # CANCELLED member (BookingStatus, LaundryStatus do; TableStatus/PaymentStatus
            # used elsewhere don't represent a booking lifecycle the same way).
            if enum_type is not None and hasattr(enum_type, "CANCELLED"):
                setattr(record, status_field, enum_type.CANCELLED)
            if getattr(record, "room", None) is not None and record.room.status.value == "not_available":
                from app.models.enums import RoomStatus
                record.room.status = RoomStatus.AVAILABLE
            if getattr(record, "table", None) is not None and record.table.status.value == "reserved":
                from app.models.enums import TableStatus
                record.table.status = TableStatus.AVAILABLE

    notify_customer(db, booking.customer_id, "Booking cancelled",
                     f"Your booking {booking.booking_code} has been cancelled as requested.")
    db.commit()
    db.refresh(booking)
    return booking


# ---------- Book a Stay (Section 10/11) ----------

@router.post("/stay-requests", response_model=StayRequestOut)
def submit_stay_request(payload: StayRequestCreate, db: Session = Depends(get_db)):
    if payload.requirement_text and len(payload.requirement_text) > 600:
        raise HTTPException(status_code=400, detail="Requirement text must be 600 characters or fewer")
    request = StayRequest(**payload.model_dump(), status=EnquiryStatus.NEW)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/stay-requests", response_model=List[StayRequestOut])
def list_stay_requests(status_filter: Optional[EnquiryStatus] = None, db: Session = Depends(get_db),
                        _=Depends(require_staff_any)):
    query = db.query(StayRequest)
    if status_filter:
        query = query.filter(StayRequest.status == status_filter)
    return query.order_by(StayRequest.id.desc()).all()


@router.put("/stay-requests/{request_id}/status", response_model=StayRequestOut)
def update_stay_request_status(request_id: int, new_status: EnquiryStatus, db: Session = Depends(get_db),
                                current_user=Depends(require_staff_any)):
    request = db.query(StayRequest).filter(StayRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Stay request not found")
    request.status = new_status
    if current_user.employee:
        request.reviewed_by_employee_id = current_user.employee.id
    db.commit()
    db.refresh(request)
    return request
