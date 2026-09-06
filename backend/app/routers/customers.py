from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_staff_any
from app.core.security import hash_password
from app.models.core import User
from app.models.customer import Customer
from app.models.enums import UserRole, UserStatus
from app.services.codes import generate_customer_code

router = APIRouter(prefix="/api/customers", tags=["Customers"])


class CustomerRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    username: str
    password: str


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    status: Optional[UserStatus] = None


class CustomerOut(BaseModel):
    id: int
    customer_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    registration_date: datetime
    status: UserStatus

    class Config:
        from_attributes = True


@router.post("/register", response_model=CustomerOut)
def register_customer(payload: CustomerRegister, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    customer = Customer(
        customer_code=generate_customer_code(db),
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        country=payload.country,
        state=payload.state,
        city=payload.city,
    )
    db.add(customer)
    db.flush()

    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
        customer_id=customer.id,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=List[CustomerOut])
def list_customers(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_staff_any),
):
    query = db.query(Customer)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Customer.first_name.ilike(like))
            | (Customer.last_name.ilike(like))
            | (Customer.email.ilike(like))
            | (Customer.phone.ilike(like))
            | (Customer.customer_code.ilike(like))
        )
    return query.order_by(Customer.id.desc()).all()


@router.get("/me", response_model=CustomerOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.customer:
        raise HTTPException(status_code=404, detail="No customer profile linked to this account")
    return current_user.customer


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), _=Depends(require_staff_any)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer
