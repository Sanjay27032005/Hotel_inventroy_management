from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Enum as SAEnum, Text
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import UserStatus


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    fee = Column(Numeric(10, 2), nullable=False)
    duration_months = Column(Integer, nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    benefits = Column(Text, nullable=True)  # room/restaurant/club/spa/pool/event benefits summary
    is_active = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)

    memberships = relationship("Membership", back_populates="plan")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    membership_code = Column(String(30), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("membership_plans.id"), nullable=False)
    start_date = Column(Date, default=date.today)
    end_date = Column(Date, nullable=False)
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)

    customer = relationship("Customer", back_populates="memberships")
    plan = relationship("MembershipPlan", back_populates="memberships")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=True)
    country = Column(String(80), nullable=True)
    state = Column(String(80), nullable=True)
    city = Column(String(80), nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)

    memberships = relationship("Membership", back_populates="customer")
    user_account = relationship("User", back_populates="customer", uselist=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
