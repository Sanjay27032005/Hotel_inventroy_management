from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import PaymentStatus, UserStatus


class ClubMembership(Base):
    __tablename__ = "club_memberships"

    id = Column(Integer, primary_key=True, index=True)
    membership_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)

    customer = relationship("Customer")


class ClubFoodItem(Base):
    __tablename__ = "club_food_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)


class ClubDrinkItem(Base):
    __tablename__ = "club_drink_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)


class ClubOrder(Base):
    __tablename__ = "club_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    club_membership_id = Column(Integer, ForeignKey("club_memberships.id"), nullable=True)

    entry_fee = Column(Numeric(10, 2), default=0)
    food_total = Column(Numeric(10, 2), default=0)
    drinks_total = Column(Numeric(10, 2), default=0)
    tips = Column(Numeric(10, 2), default=0)
    service_charges = Column(Numeric(10, 2), default=0)
    membership_discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)

    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    club_membership = relationship("ClubMembership")
    items = relationship("ClubOrderItem", back_populates="order", cascade="all, delete-orphan")


class ClubOrderItem(Base):
    __tablename__ = "club_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("club_orders.id"), nullable=False)
    item_type = Column(String(10), nullable=False)  # "food" or "drink"
    food_item_id = Column(Integer, ForeignKey("club_food_items.id"), nullable=True)
    drink_item_id = Column(Integer, ForeignKey("club_drink_items.id"), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    order = relationship("ClubOrder", back_populates="items")
    food_item = relationship("ClubFoodItem")
    drink_item = relationship("ClubDrinkItem")
