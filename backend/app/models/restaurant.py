from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SAEnum, Boolean, Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import TableStatus, OrderStatus, PaymentStatus


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    table_type = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)
    status = Column(SAEnum(TableStatus), default=TableStatus.AVAILABLE)

    bookings = relationship("RestaurantBooking", back_populates="table")


class RestaurantBooking(Base):
    __tablename__ = "restaurant_bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=False)
    booking_type = Column(String(20), default="instant")  # pre_booking / instant
    reserved_for = Column(DateTime, nullable=False)
    party_size = Column(Integer, default=2)
    status = Column(SAEnum(TableStatus), default=TableStatus.RESERVED)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    table = relationship("RestaurantTable", back_populates="bookings")


class FoodCategory(Base):
    __tablename__ = "food_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Indian, Biriyani, Desserts, etc.
    meal_category = Column(String(20), nullable=True)  # breakfast/lunch/evening/dinner

    items = relationship("FoodItem", back_populates="category")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category_id = Column(Integer, ForeignKey("food_categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    tax_percentage = Column(Numeric(5, 2), default=5)
    image_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)

    category = relationship("FoodCategory", back_populates="items")


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=True)

    subtotal = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)

    status = Column(SAEnum(OrderStatus), default=OrderStatus.NEW)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    table = relationship("RestaurantTable")
    items = relationship("FoodOrderItem", back_populates="order", cascade="all, delete-orphan")


class FoodOrderItem(Base):
    __tablename__ = "food_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("food_orders.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # quantity * unit_price

    order = relationship("FoodOrder", back_populates="items")
    food_item = relationship("FoodItem")
