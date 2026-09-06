from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.club import ClubMembership, ClubFoodItem, ClubDrinkItem, ClubOrder, ClubOrderItem
from app.models.enums import PaymentStatus, UserStatus
from app.services.codes import generate_sub_booking_code, money
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/club", tags=["Club & Bar"])


class ClubMembershipCreate(BaseModel):
    customer_id: int
    plan_name: str
    discount_percentage: float = 0


class ClubMembershipOut(ClubMembershipCreate):
    id: int
    membership_code: str
    status: UserStatus

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    name: str
    unit_price: float


class FoodItemOut(MenuItemCreate):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class DrinkItemOut(MenuItemCreate):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class OrderLine(BaseModel):
    item_type: str  # "food" or "drink"
    item_id: int
    quantity: int = 1


class ClubOrderCreate(BaseModel):
    customer_id: int
    club_membership_id: Optional[int] = None
    entry_fee: float = 0
    lines: List[OrderLine] = []
    tips: float = 0
    service_charges: float = 0
    tax: float = 0


class ClubOrderItemOut(BaseModel):
    id: int
    item_type: str
    quantity: int
    unit_price: float
    amount: float

    class Config:
        from_attributes = True


class ClubOrderOut(BaseModel):
    id: int
    order_code: str
    customer_id: int
    entry_fee: float
    food_total: float
    drinks_total: float
    tips: float
    service_charges: float
    membership_discount: float
    tax: float
    total_amount: float
    payment_status: PaymentStatus
    items: List[ClubOrderItemOut]

    class Config:
        from_attributes = True


@router.post("/memberships", response_model=ClubMembershipOut)
def create_club_membership(payload: ClubMembershipCreate, db: Session = Depends(get_db),
                            _=Depends(require_staff_any)):
    membership = ClubMembership(
        membership_code=generate_sub_booking_code(db, ClubMembership, ClubMembership.membership_code, "CLB"),
        **payload.model_dump(),
        status=UserStatus.ACTIVE,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.get("/food-items", response_model=List[FoodItemOut])
def list_food_items(db: Session = Depends(get_db)):
    return db.query(ClubFoodItem).filter(ClubFoodItem.is_available == True).all()  # noqa: E712


@router.post("/food-items", response_model=FoodItemOut)
def create_food_item(payload: MenuItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    item = ClubFoodItem(**payload.model_dump(), is_available=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/drink-items", response_model=List[DrinkItemOut])
def list_drink_items(db: Session = Depends(get_db)):
    return db.query(ClubDrinkItem).filter(ClubDrinkItem.is_available == True).all()  # noqa: E712


@router.post("/drink-items", response_model=DrinkItemOut)
def create_drink_item(payload: MenuItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    item = ClubDrinkItem(**payload.model_dump(), is_available=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/orders", response_model=ClubOrderOut)
def create_club_order(payload: ClubOrderCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    membership = None
    if payload.club_membership_id:
        membership = db.query(ClubMembership).filter(ClubMembership.id == payload.club_membership_id).first()
        if not membership or membership.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Membership is not active")

    order = ClubOrder(
        order_code=generate_sub_booking_code(db, ClubOrder, ClubOrder.order_code, "CO"),
        customer_id=payload.customer_id,
        club_membership_id=payload.club_membership_id,
        entry_fee=payload.entry_fee,
        tips=payload.tips,
        service_charges=payload.service_charges,
        tax=payload.tax,
        payment_status=PaymentStatus.PENDING,
    )
    db.add(order)
    db.flush()

    food_total = Decimal("0")
    drinks_total = Decimal("0")
    for line in payload.lines:
        if line.item_type == "food":
            item = db.query(ClubFoodItem).filter(ClubFoodItem.id == line.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Food item not found")
            amount = Decimal(str(item.unit_price)) * line.quantity
            food_total += amount
            db.add(ClubOrderItem(order_id=order.id, item_type="food", food_item_id=item.id,
                                  quantity=line.quantity, unit_price=item.unit_price, amount=amount))
        elif line.item_type == "drink":
            item = db.query(ClubDrinkItem).filter(ClubDrinkItem.id == line.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Drink item not found")
            amount = Decimal(str(item.unit_price)) * line.quantity
            drinks_total += amount
            db.add(ClubOrderItem(order_id=order.id, item_type="drink", drink_item_id=item.id,
                                  quantity=line.quantity, unit_price=item.unit_price, amount=amount))
        else:
            raise HTTPException(status_code=400, detail="item_type must be 'food' or 'drink'")

    # Billing Calculation per Section 25/33:
    # Subtotal + Entry Fee + Food + Drinks + Tips + Service Charges - Membership Discount + Tax = Grand Total
    subtotal = Decimal(str(payload.entry_fee)) + food_total + drinks_total + \
        Decimal(str(payload.tips)) + Decimal(str(payload.service_charges))
    membership_discount = Decimal("0")
    if membership:
        membership_discount = subtotal * (Decimal(str(membership.discount_percentage)) / 100)

    order.food_total = food_total
    order.drinks_total = drinks_total
    order.membership_discount = money(membership_discount)
    order.total_amount = money(subtotal - membership_discount + Decimal(str(payload.tax)))

    notify_customer(db, payload.customer_id, "Club order placed",
                     f"Your club & bar order {order.order_code} has been recorded.")
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=List[ClubOrderOut])
def list_club_orders(customer_id: Optional[int] = None, db: Session = Depends(get_db),
                      _=Depends(get_current_user)):
    query = db.query(ClubOrder)
    if customer_id:
        query = query.filter(ClubOrder.customer_id == customer_id)
    return query.order_by(ClubOrder.id.desc()).all()
