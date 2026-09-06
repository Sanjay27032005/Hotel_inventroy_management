from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole, UserStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    username: str
    display_name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole
    status: UserStatus
    employee_id: Optional[int] = None
    customer_id: Optional[int] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole
    employee_id: Optional[int] = None
    customer_id: Optional[int] = None
