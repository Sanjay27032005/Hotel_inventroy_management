from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import UserRole, UserStatus


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(UserRole), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    hire_date = Column(Date, default=date.today)
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
    user_account = relationship("User", back_populates="employee", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_locked = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="user_account")
    customer = relationship("Customer", back_populates="user_account")

    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
