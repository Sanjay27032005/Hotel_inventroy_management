from datetime import date, timedelta
from typing import Optional, List

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.core import User
from app.models.customer import MembershipPlan, Membership
from app.models.enums import UserStatus
from app.services.codes import generate_membership_code

router = APIRouter(prefix="/api/membership", tags=["Membership"])


class PlanCreate(BaseModel):
    name: str
    fee: float
    duration_months: int
    discount_percentage: float = 0
    benefits: Optional[str] = None


class PlanOut(BaseModel):
    id: int
    name: str
    fee: float
    duration_months: int
    discount_percentage: float
    benefits: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipEnroll(BaseModel):
    customer_id: int
    plan_id: int


class MembershipOut(BaseModel):
    id: int
    membership_code: str
    customer_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: UserStatus

    class Config:
        from_attributes = True


@router.get("/plans", response_model=List[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(MembershipPlan).all()


@router.post("/plans", response_model=PlanOut)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    plan = MembershipPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/enroll", response_model=MembershipOut)
def enroll_member(payload: MembershipEnroll, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == payload.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Membership plan not found")

    start = date.today()
    end = start + relativedelta(months=plan.duration_months)

    membership = Membership(
        membership_code=generate_membership_code(db),
        customer_id=payload.customer_id,
        plan_id=payload.plan_id,
        start_date=start,
        end_date=end,
        status=UserStatus.ACTIVE,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.get("/customer/{customer_id}", response_model=List[MembershipOut])
def get_customer_memberships(customer_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Membership).filter(Membership.customer_id == customer_id).all()
