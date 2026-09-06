from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import LaundryPricingMethod, LaundryStatus, PaymentStatus


class LaundryServicePrice(Base):
    """Admin-configurable per-cloth-type price (used for both cloth-based and quantity-based billing)."""
    __tablename__ = "laundry_service_prices"

    id = Column(Integer, primary_key=True, index=True)
    cloth_type = Column(String(50), unique=True, nullable=False)  # Shirt, Pant, T-Shirt, Suit, Saree, Jacket, Other
    unit_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)


class LaundryOrder(Base):
    __tablename__ = "laundry_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    room_number = Column(String(20), nullable=True)

    pricing_method = Column(SAEnum(LaundryPricingMethod), default=LaundryPricingMethod.QUANTITY_BASED)
    pickup_date = Column(Date, default=date.today)
    delivery_date = Column(Date, nullable=True)

    subtotal = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)

    status = Column(SAEnum(LaundryStatus), default=LaundryStatus.RECEIVED)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    items = relationship("LaundryOrderItem", back_populates="order", cascade="all, delete-orphan")


class LaundryOrderItem(Base):
    __tablename__ = "laundry_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("laundry_orders.id"), nullable=False)
    cloth_type = Column(String(50), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    order = relationship("LaundryOrder", back_populates="items")
