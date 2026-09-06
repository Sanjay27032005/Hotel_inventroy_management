from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_billing, require_staff_any
from app.models.booking_billing import Invoice, InvoiceItem, Payment
from app.models.customer import Customer
from app.models.enums import InvoiceServiceType, PaymentMethod, PaymentStatus
from app.services.codes import generate_invoice_number, generate_payment_code
from app.services.invoice_pdf import build_invoice_pdf
from app.services.notifications import notify_customer
from app.services.audit import log_action

router = APIRouter(prefix="/api/billing", tags=["Billing"])


# ---------- Schemas ----------

class InvoiceItemOut(BaseModel):
    id: int
    description: str
    quantity: float
    rate: float
    amount: float

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    booking_code: Optional[str] = None
    customer_id: int
    service_type: InvoiceServiceType
    reference_id: int
    subtotal: float
    discount: float
    tax: float
    additional_charges: float
    grand_total: float
    payment_method: Optional[PaymentMethod] = None
    payment_status: PaymentStatus
    created_at: datetime
    items: List[InvoiceItemOut]

    class Config:
        from_attributes = True


class InvoiceGenerate(BaseModel):
    service_type: InvoiceServiceType
    reference_id: int


class PaymentCreate(BaseModel):
    invoice_id: int
    amount_paid: float
    payment_method: PaymentMethod


class PaymentOut(BaseModel):
    id: int
    payment_code: str
    invoice_id: int
    amount_paid: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    paid_at: datetime

    class Config:
        from_attributes = True


# ---------- Service lookup: pulls totals + line items from the underlying service record ----------

def _load_service_record(db: Session, service_type: InvoiceServiceType, reference_id: int):
    from app.models.restaurant import FoodOrder
    from app.models.accommodation import RoomBooking
    from app.models.events import EventBooking
    from app.models.pool import PoolBooking
    from app.models.spa import SpaBooking
    from app.models.club import ClubOrder
    from app.models.laundry import LaundryOrder

    mapping = {
        InvoiceServiceType.RESTAURANT: FoodOrder,
        InvoiceServiceType.ACCOMMODATION: RoomBooking,
        InvoiceServiceType.PARTY_HALL: EventBooking,
        InvoiceServiceType.SWIMMING_POOL: PoolBooking,
        InvoiceServiceType.SPA: SpaBooking,
        InvoiceServiceType.CLUB_BAR: ClubOrder,
        InvoiceServiceType.LAUNDRY: LaundryOrder,
    }
    model = mapping[service_type]
    record = db.query(model).filter(model.id == reference_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"No {service_type.value} record found with id {reference_id}")
    return record


def _build_invoice_lines(service_type: InvoiceServiceType, record):
    """Returns (customer_id, booking_code, subtotal, discount, tax, additional_charges, grand_total, line_items)."""
    booking_code = getattr(record, "booking_code", None) or getattr(record, "order_code", None)

    if service_type == InvoiceServiceType.RESTAURANT:
        lines = [(f"{it.food_item.name}", float(it.quantity), float(it.unit_price), float(it.amount))
                 for it in record.items]
        return (record.customer_id, booking_code, float(record.subtotal), float(record.discount),
                float(record.tax), 0.0, float(record.total_amount), lines)

    if service_type == InvoiceServiceType.ACCOMMODATION:
        lines = [(f"Room {record.room.room_number} ({record.rate_type.value})", float(record.duration),
                   float(record.room_rate), float(record.room_rate) * float(record.duration))]
        subtotal = float(record.room_rate) * float(record.duration)
        return (record.customer_id, booking_code, subtotal, float(record.discount), float(record.tax), 0.0,
                float(record.total_amount), lines)

    if service_type == InvoiceServiceType.PARTY_HALL:
        lines = [("Hall charges", float(record.duration), float(record.hall_charges) / max(float(record.duration), 1),
                   float(record.hall_charges))]
        if record.additional_services_charge:
            lines.append(("Additional services", 1, float(record.additional_services_charge),
                          float(record.additional_services_charge)))
        subtotal = float(record.hall_charges)
        return (record.customer_id, booking_code, subtotal, float(record.discount), float(record.tax),
                float(record.additional_services_charge), float(record.total_amount), lines)

    if service_type == InvoiceServiceType.SWIMMING_POOL:
        lines = [(f"{record.package_type.value.title()} package ({record.customer_type.value})", 1,
                   float(record.package_amount), float(record.package_amount))]
        return (record.customer_id, booking_code, float(record.package_amount), float(record.discount),
                float(record.tax), 0.0, float(record.total_amount), lines)

    if service_type == InvoiceServiceType.SPA:
        lines = [(f"{record.spa_service.name} ({record.duration_minutes} min)", 1, float(record.amount),
                   float(record.amount))]
        return (record.customer_id, booking_code, float(record.amount), float(record.discount),
                float(record.tax), 0.0, float(record.total_amount), lines)

    if service_type == InvoiceServiceType.CLUB_BAR:
        lines = []
        if record.entry_fee:
            lines.append(("Club entry fee", 1, float(record.entry_fee), float(record.entry_fee)))
        for it in record.items:
            name = it.food_item.name if it.item_type == "food" else it.drink_item.name
            lines.append((name, float(it.quantity), float(it.unit_price), float(it.amount)))
        if record.tips:
            lines.append(("Tips", 1, float(record.tips), float(record.tips)))
        if record.service_charges:
            lines.append(("Service charges", 1, float(record.service_charges), float(record.service_charges)))
        subtotal = float(record.entry_fee) + float(record.food_total) + float(record.drinks_total) + \
            float(record.tips) + float(record.service_charges)
        return (record.customer_id, booking_code, subtotal, float(record.membership_discount),
                float(record.tax), 0.0, float(record.total_amount), lines)

    if service_type == InvoiceServiceType.LAUNDRY:
        lines = [(f"{it.cloth_type}", it.quantity, float(it.unit_price), float(it.amount)) for it in record.items]
        return (record.customer_id, booking_code, float(record.subtotal), float(record.discount),
                float(record.tax), 0.0, float(record.total_amount), lines)

    raise HTTPException(status_code=400, detail="Unsupported service type")


@router.post("/invoices/generate", response_model=InvoiceOut)
def generate_invoice(payload: InvoiceGenerate, db: Session = Depends(get_db),
                      current_user=Depends(require_billing)):
    existing = db.query(Invoice).filter(
        Invoice.service_type == payload.service_type, Invoice.reference_id == payload.reference_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="An invoice already exists for this booking/order")

    record = _load_service_record(db, payload.service_type, payload.reference_id)
    customer_id, booking_code, subtotal, discount, tax, additional, grand_total, lines = \
        _build_invoice_lines(payload.service_type, record)

    invoice = Invoice(
        invoice_number=generate_invoice_number(db),
        booking_code=booking_code,
        customer_id=customer_id,
        service_type=payload.service_type,
        reference_id=payload.reference_id,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        additional_charges=additional,
        grand_total=grand_total,
        payment_status=PaymentStatus.PENDING,
        generated_by_employee_id=current_user.employee.id if current_user.employee else None,
    )
    db.add(invoice)
    db.flush()

    for description, quantity, rate, amount in lines:
        db.add(InvoiceItem(invoice_id=invoice.id, description=description, quantity=quantity,
                            rate=rate, amount=amount))

    log_action(db, current_user, "invoice_generated",
               details=f"invoice={invoice.invoice_number} service={payload.service_type.value}")
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices", response_model=List[InvoiceOut])
def list_invoices(customer_id: Optional[int] = None, service_type: Optional[InvoiceServiceType] = None,
                   payment_status: Optional[PaymentStatus] = None,
                   db: Session = Depends(get_db), _=Depends(require_staff_any)):
    query = db.query(Invoice)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    if service_type:
        query = query.filter(Invoice.service_type == service_type)
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    return query.order_by(Invoice.id.desc()).all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Printable invoice (Section 15/21/63): hotel details, line items, subtotal/discount/
    tax/additional charges/grand total, and payment method/status, as a downloadable PDF."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    pdf_bytes = build_invoice_pdf(invoice, customer, invoice.items)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{invoice.invoice_number}.pdf"'},
    )


def _sync_underlying_payment_status(db: Session, invoice: Invoice):
    """Reflect the invoice's payment status back onto the originating service record."""
    from app.models.restaurant import FoodOrder
    from app.models.accommodation import RoomBooking
    from app.models.events import EventBooking
    from app.models.pool import PoolBooking
    from app.models.spa import SpaBooking
    from app.models.club import ClubOrder
    from app.models.laundry import LaundryOrder

    mapping = {
        InvoiceServiceType.RESTAURANT: FoodOrder,
        InvoiceServiceType.ACCOMMODATION: RoomBooking,
        InvoiceServiceType.PARTY_HALL: EventBooking,
        InvoiceServiceType.SWIMMING_POOL: PoolBooking,
        InvoiceServiceType.SPA: SpaBooking,
        InvoiceServiceType.CLUB_BAR: ClubOrder,
        InvoiceServiceType.LAUNDRY: LaundryOrder,
    }
    model = mapping.get(invoice.service_type)
    if not model:
        return
    record = db.query(model).filter(model.id == invoice.reference_id).first()
    if record is not None:
        record.payment_status = invoice.payment_status


@router.post("/payments", response_model=PaymentOut)
def process_payment(payload: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(require_billing)):
    invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.payment_status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="This invoice is already fully paid")

    already_paid = sum(float(p.amount_paid) for p in invoice.payments if p.payment_status == PaymentStatus.PAID)
    total_after = already_paid + payload.amount_paid

    payment = Payment(
        payment_code=generate_payment_code(db),
        invoice_id=invoice.id,
        amount_paid=payload.amount_paid,
        payment_method=payload.payment_method,
        payment_status=PaymentStatus.PAID,
        processed_by_employee_id=current_user.employee.id if current_user.employee else None,
    )
    db.add(payment)

    if total_after >= float(invoice.grand_total):
        invoice.payment_status = PaymentStatus.PAID
    else:
        invoice.payment_status = PaymentStatus.PARTIALLY_PAID
    invoice.payment_method = payload.payment_method

    _sync_underlying_payment_status(db, invoice)

    if invoice.payment_status == PaymentStatus.PAID:
        notify_customer(db, invoice.customer_id, "Payment received",
                         f"We've received full payment for invoice {invoice.invoice_number}.")
    log_action(db, current_user, "payment_recorded",
               details=f"invoice={invoice.invoice_number} amount={payload.amount_paid} method={payload.payment_method.value}")
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/invoices/{invoice_id}/refund", response_model=InvoiceOut)
def refund_invoice(invoice_id: int, db: Session = Depends(get_db), current_user=Depends(require_billing)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.payment_status = PaymentStatus.REFUNDED
    _sync_underlying_payment_status(db, invoice)
    notify_customer(db, invoice.customer_id, "Payment refunded",
                     f"Invoice {invoice.invoice_number} has been refunded.")
    log_action(db, current_user, "invoice_refunded", details=f"invoice={invoice.invoice_number}")
    db.commit()
    db.refresh(invoice)
    return invoice
