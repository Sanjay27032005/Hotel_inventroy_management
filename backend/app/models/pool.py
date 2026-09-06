from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import PoolCustomerType, PoolPackageType, BookingStatus, PaymentStatus


class PoolPackagePrice(Base):
    """Admin-configurable price matrix: customer_type x package_type."""
    __tablename__ = "pool_package_prices"

    id = Column(Integer, primary_key=True, index=True)
    customer_type = Column(SAEnum(PoolCustomerType), nullable=False)
    package_type = Column(SAEnum(PoolPackageType), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)


class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)


class PoolBooking(Base):
    __tablename__ = "pool_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer_type = Column(SAEnum(PoolCustomerType), nullable=False)
    package_type = Column(SAEnum(PoolPackageType), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=True)

    booking_date = Column(DateTime, nullable=False)
    package_amount = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    booking_status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    trainer = relationship("Trainer")
