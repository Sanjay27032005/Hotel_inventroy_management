from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import (
    BookingType, BookingStatus, InvoiceServiceType, PaymentMethod, PaymentStatus, EnquiryStatus
)


class Booking(Base):
    """Centralized booking registry: one row per booking regardless of service type,
    referencing the specific service booking row via booking_type + reference_id."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)  # BK-2026-000001
    booking_type = Column(SAEnum(BookingType), nullable=False)
    reference_id = Column(Integer, nullable=False)  # id in the specific booking table
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")


class StayRequest(Base):
    """'Book a Stay' home-page enquiry form (Section 10/11 of the requirement doc)."""
    __tablename__ = "stay_requests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    requirement_text = Column(String(600), nullable=True)  # "Ask Us What You Need" — max 600 chars
    status = Column(SAEnum(EnquiryStatus), default=EnquiryStatus.NEW)
    reviewed_by_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviewed_by = relationship("Employee")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(30), unique=True, index=True, nullable=False)
    booking_code = Column(String(30), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    service_type = Column(SAEnum(InvoiceServiceType), nullable=False)
    reference_id = Column(Integer, nullable=False)  # id of the service order/booking this invoice covers

    subtotal = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    additional_charges = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(10, 2), default=0)

    payment_method = Column(SAEnum(PaymentMethod), nullable=True)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)

    generated_by_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    generated_by = relationship("Employee")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), default=1)
    rate = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_code = Column(String(30), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SAEnum(PaymentMethod), nullable=False)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PAID)
    processed_by_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    paid_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="payments")
    processed_by = relationship("Employee")
