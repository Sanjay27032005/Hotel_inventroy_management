from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Text, Time
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import RoomStatus, RoomCustomerCategory, RateType, BookingStatus, PaymentStatus


class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Standard Single, Superior Twin, etc.
    customer_category = Column(SAEnum(RoomCustomerCategory), nullable=False)
    description = Column(Text, nullable=True)
    hourly_rate = Column(Numeric(10, 2), default=0)
    daily_rate = Column(Numeric(10, 2), default=0)
    weekly_rate = Column(Numeric(10, 2), default=0)
    monthly_rate = Column(Numeric(10, 2), default=0)
    max_adults = Column(Integer, default=2)
    max_children = Column(Integer, default=1)

    rooms = relationship("Room", back_populates="room_type")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), unique=True, nullable=False)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    floor = Column(String(20), nullable=True)
    status = Column(SAEnum(RoomStatus), default=RoomStatus.AVAILABLE)

    room_type = relationship("RoomType", back_populates="rooms")
    bookings = relationship("RoomBooking", back_populates="room")


class RoomBooking(Base):
    __tablename__ = "room_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    check_in_date = Column(DateTime, nullable=False)
    check_in_time = Column(Time, nullable=True)
    check_out_date = Column(DateTime, nullable=False)
    check_out_time = Column(Time, nullable=True)

    adults = Column(Integer, default=1)
    children = Column(Integer, default=0)
    rate_type = Column(SAEnum(RateType), default=RateType.DAILY)
    room_rate = Column(Numeric(10, 2), nullable=False)
    duration = Column(Numeric(10, 2), nullable=False)  # hours/days/weeks/months depending on rate_type

    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    booking_status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)

    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    room = relationship("Room", back_populates="bookings")
