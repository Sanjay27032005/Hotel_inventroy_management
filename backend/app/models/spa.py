from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, Time, ForeignKey, Numeric, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import BookingStatus, PaymentStatus


class SpaService(Base):
    __tablename__ = "spa_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Traditional Massage, Thai Massage, etc.
    description = Column(String(255), nullable=True)
    service_price = Column(Numeric(10, 2), nullable=False)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)


class Therapist(Base):
    __tablename__ = "therapists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)


class SpaBooking(Base):
    __tablename__ = "spa_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    spa_service_id = Column(Integer, ForeignKey("spa_services.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("therapists.id"), nullable=True)

    booking_date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    booking_status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    spa_service = relationship("SpaService")
    therapist = relationship("Therapist")
