from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import RateType, BookingStatus, PaymentStatus


class EventType(Base):
    __tablename__ = "event_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)  # Birthday, Wedding, Office Party, etc.


class PartyHall(Base):
    __tablename__ = "party_halls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    location = Column(String(150), nullable=True)
    facilities = Column(Text, nullable=True)
    hourly_rate = Column(Numeric(10, 2), default=0)
    daily_rate = Column(Numeric(10, 2), default=0)
    weekly_rate = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="available")

    bookings = relationship("EventBooking", back_populates="hall")


class EventBooking(Base):
    __tablename__ = "event_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("party_halls.id"), nullable=False)
    event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)

    event_date = Column(DateTime, nullable=False)
    rate_type = Column(SAEnum(RateType), default=RateType.DAILY)
    duration = Column(Numeric(10, 2), nullable=False)
    hall_charges = Column(Numeric(10, 2), nullable=False)
    additional_services_charge = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    booking_status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    hall = relationship("PartyHall", back_populates="bookings")
    event_type = relationship("EventType")
