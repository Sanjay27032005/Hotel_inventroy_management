from datetime import date
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_staff_any
from app.models.laundry import LaundryServicePrice, LaundryOrder, LaundryOrderItem
from app.models.enums import LaundryPricingMethod, LaundryStatus, PaymentStatus
from app.services.codes import generate_sub_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/laundry", tags=["Laundry"])


class ClothPriceSet(BaseModel):
    cloth_type: str
    unit_price: float


class ClothPriceOut(ClothPriceSet):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class LaundryLine(BaseModel):
    cloth_type: str
    quantity: int = 1


class LaundryOrderCreate(BaseModel):
    customer_id: int
    room_number: Optional[str] = None
    pricing_method: LaundryPricingMethod = LaundryPricingMethod.QUANTITY_BASED
    items: List[LaundryLine]
    delivery_date: Optional[date] = None
    discount: float = 0
    tax: float = 0


class LaundryOrderItemOut(BaseModel):
    id: int
    cloth_type: str
    quantity: int
    unit_price: float
    amount: float

    class Config:
        from_attributes = True


class LaundryOrderOut(BaseModel):
    id: int
    order_code: str
    customer_id: int
    room_number: Optional[str] = None
    pricing_method: LaundryPricingMethod
    pickup_date: date
    delivery_date: Optional[date] = None
    subtotal: float
    discount: float
    tax: float
    total_amount: float
    status: LaundryStatus
    payment_status: PaymentStatus
    items: List[LaundryOrderItemOut]

    class Config:
        from_attributes = True


@router.get("/prices", response_model=List[ClothPriceOut])
def list_cloth_prices(db: Session = Depends(get_db)):
    return db.query(LaundryServicePrice).filter(LaundryServicePrice.is_active == True).all()  # noqa: E712


@router.put("/prices", response_model=ClothPriceOut)
def set_cloth_price(payload: ClothPriceSet, db: Session = Depends(get_db), _=Depends(require_admin)):
    existing = db.query(LaundryServicePrice).filter(
        LaundryServicePrice.cloth_type == payload.cloth_type
    ).first()
    if existing:
        existing.unit_price = payload.unit_price
        db.commit()
        db.refresh(existing)
        return existing
    price = LaundryServicePrice(**payload.model_dump(), is_active=True)
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


@router.post("/orders", response_model=LaundryOrderOut)
def create_laundry_order(payload: LaundryOrderCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="A laundry order must contain at least one item")

    order = LaundryOrder(
        order_code=generate_sub_booking_code(db, LaundryOrder, LaundryOrder.order_code, "LN"),
        customer_id=payload.customer_id,
        room_number=payload.room_number,
        pricing_method=payload.pricing_method,
        delivery_date=payload.delivery_date,
        discount=payload.discount,
        tax=payload.tax,
        status=LaundryStatus.RECEIVED,
        payment_status=PaymentStatus.PENDING,
    )
    db.add(order)
    db.flush()

    subtotal = Decimal("0")
    for line in payload.items:
        price_row = db.query(LaundryServicePrice).filter(
            LaundryServicePrice.cloth_type == line.cloth_type
        ).first()
        if not price_row:
            raise HTTPException(status_code=400, detail=f"No price configured for cloth type '{line.cloth_type}'")
        # Cloth-based pricing charges a flat unit price regardless of quantity beyond 1;
        # quantity-based pricing multiplies by quantity (Section 35/26 of the requirement doc).
        qty = line.quantity if payload.pricing_method == LaundryPricingMethod.QUANTITY_BASED else 1
        amount = Decimal(str(price_row.unit_price)) * qty
        subtotal += amount
        db.add(LaundryOrderItem(
            order_id=order.id, cloth_type=line.cloth_type, quantity=line.quantity,
            unit_price=price_row.unit_price, amount=amount,
        ))

    total_discount = apply_membership_discount(db, payload.customer_id, subtotal, payload.discount)
    order.discount = total_discount
    order.subtotal = subtotal
    order.total_amount = calculate_grand_total(subtotal, payload.tax, total_discount)
    notify_customer(db, payload.customer_id, "Laundry order received",
                     f"Your laundry order {order.order_code} has been received.")
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=List[LaundryOrderOut])
def list_laundry_orders(customer_id: Optional[int] = None, status_filter: Optional[LaundryStatus] = None,
                         db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(LaundryOrder)
    if customer_id:
        query = query.filter(LaundryOrder.customer_id == customer_id)
    if status_filter:
        query = query.filter(LaundryOrder.status == status_filter)
    return query.order_by(LaundryOrder.id.desc()).all()


@router.put("/orders/{order_id}/status", response_model=LaundryOrderOut)
def update_laundry_status(order_id: int, new_status: LaundryStatus, db: Session = Depends(get_db),
                           _=Depends(require_staff_any)):
    """Received -> Washing -> Drying -> Ironing -> Ready -> Delivered (Section 35)."""
    order = db.query(LaundryOrder).filter(LaundryOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Laundry order not found")
    order.status = new_status
    if new_status == LaundryStatus.READY:
        notify_customer(db, order.customer_id, "Laundry ready",
                         f"Your laundry order {order.order_code} is ready for delivery.")
    db.commit()
    db.refresh(order)
    return order
