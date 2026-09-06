from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import (
    get_current_user, require_admin, require_management, require_staff_any,
    require_food_staff, require_kitchen_staff,
)
from app.models.booking_billing import Booking
from app.models.restaurant import (
    RestaurantTable, RestaurantBooking, FoodCategory, FoodItem, FoodOrder, FoodOrderItem,
)
from app.models.enums import TableStatus, OrderStatus, PaymentStatus, BookingType, BookingStatus
from app.services.codes import generate_sub_booking_code, generate_booking_code, calculate_grand_total
from app.services.membership_discount import apply_membership_discount
from app.services.notifications import notify_customer

router = APIRouter(prefix="/api/restaurant", tags=["Restaurant"])


# ---------- Schemas ----------

class TableCreate(BaseModel):
    table_number: str
    capacity: int
    table_type: Optional[str] = None
    location: Optional[str] = None


class TableOut(BaseModel):
    id: int
    table_number: str
    capacity: int
    table_type: Optional[str] = None
    location: Optional[str] = None
    status: TableStatus

    class Config:
        from_attributes = True


class TableBookingCreate(BaseModel):
    customer_id: int
    table_id: int
    booking_type: str = "instant"  # pre_booking / instant
    reserved_for: datetime
    party_size: int = 2


class TableBookingOut(BaseModel):
    id: int
    booking_code: str
    customer_id: int
    table_id: int
    booking_type: str
    reserved_for: datetime
    party_size: int
    status: TableStatus

    class Config:
        from_attributes = True


class FoodCategoryCreate(BaseModel):
    name: str
    meal_category: Optional[str] = None


class FoodCategoryOut(FoodCategoryCreate):
    id: int

    class Config:
        from_attributes = True


class FoodItemCreate(BaseModel):
    name: str
    category_id: int
    description: Optional[str] = None
    price: float
    tax_percentage: float = 5
    image_url: Optional[str] = None


class FoodItemOut(FoodItemCreate):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class OrderItemIn(BaseModel):
    food_item_id: int
    quantity: int = 1


class FoodOrderCreate(BaseModel):
    customer_id: int
    table_id: Optional[int] = None
    items: List[OrderItemIn]
    discount: float = 0


class FoodOrderItemOut(BaseModel):
    id: int
    food_item_id: int
    quantity: int
    unit_price: float
    amount: float

    class Config:
        from_attributes = True


class FoodOrderOut(BaseModel):
    id: int
    order_code: str
    customer_id: int
    table_id: Optional[int] = None
    subtotal: float
    discount: float
    tax: float
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    items: List[FoodOrderItemOut]

    class Config:
        from_attributes = True


# ---------- Tables ----------

@router.get("/tables", response_model=List[TableOut])
def list_tables(status_filter: Optional[TableStatus] = None, db: Session = Depends(get_db)):
    query = db.query(RestaurantTable)
    if status_filter:
        query = query.filter(RestaurantTable.status == status_filter)
    return query.all()


@router.post("/tables", response_model=TableOut)
def create_table(payload: TableCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(RestaurantTable).filter(RestaurantTable.table_number == payload.table_number).first():
        raise HTTPException(status_code=400, detail="Table number already exists")
    table = RestaurantTable(**payload.model_dump(), status=TableStatus.AVAILABLE)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.put("/tables/{table_id}/status", response_model=TableOut)
def update_table_status(table_id: int, new_status: TableStatus, db: Session = Depends(get_db),
                         _=Depends(require_staff_any)):
    table = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    table.status = new_status
    db.commit()
    db.refresh(table)
    return table


# ---------- Table Bookings ----------

@router.post("/bookings", response_model=TableBookingOut)
def book_table(payload: TableBookingCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    table = db.query(RestaurantTable).filter(RestaurantTable.id == payload.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    if table.status not in (TableStatus.AVAILABLE,):
        raise HTTPException(status_code=409, detail="Table is not available")

    booking = RestaurantBooking(
        booking_code=generate_sub_booking_code(db, RestaurantBooking, RestaurantBooking.booking_code, "RB"),
        customer_id=payload.customer_id,
        table_id=payload.table_id,
        booking_type=payload.booking_type,
        reserved_for=payload.reserved_for,
        party_size=payload.party_size,
        status=TableStatus.RESERVED,
    )
    db.add(booking)
    table.status = TableStatus.RESERVED
    db.flush()

    central = Booking(
        booking_code=generate_booking_code(db),
        booking_type=BookingType.DINING_TABLE,
        reference_id=booking.id,
        customer_id=payload.customer_id,
        status=BookingStatus.CONFIRMED,
    )
    db.add(central)
    notify_customer(db, payload.customer_id, "Table reserved",
                     f"Your table reservation {booking.booking_code} is confirmed for {payload.reserved_for}.")
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=List[TableBookingOut])
def list_table_bookings(customer_id: Optional[int] = None, db: Session = Depends(get_db),
                         _=Depends(get_current_user)):
    query = db.query(RestaurantBooking)
    if customer_id:
        query = query.filter(RestaurantBooking.customer_id == customer_id)
    return query.order_by(RestaurantBooking.id.desc()).all()


# ---------- Menu ----------

@router.get("/categories", response_model=List[FoodCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(FoodCategory).all()


@router.post("/categories", response_model=FoodCategoryOut)
def create_category(payload: FoodCategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    category = FoodCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/menu", response_model=List[FoodItemOut])
def list_menu(category_id: Optional[int] = None, meal_category: Optional[str] = None,
              db: Session = Depends(get_db)):
    query = db.query(FoodItem).filter(FoodItem.is_available == True)  # noqa: E712
    if category_id:
        query = query.filter(FoodItem.category_id == category_id)
    if meal_category:
        query = query.join(FoodCategory).filter(FoodCategory.meal_category == meal_category)
    return query.all()


@router.post("/menu", response_model=FoodItemOut)
def create_food_item(payload: FoodItemCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    item = FoodItem(**payload.model_dump(), is_available=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ---------- Food Orders ----------

@router.post("/orders", response_model=FoodOrderOut)
def create_food_order(payload: FoodOrderCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="An order must contain at least one item")

    order = FoodOrder(
        order_code=generate_sub_booking_code(db, FoodOrder, FoodOrder.order_code, "ORD"),
        customer_id=payload.customer_id,
        table_id=payload.table_id,
        status=OrderStatus.NEW,
        payment_status=PaymentStatus.PENDING,
    )
    db.add(order)
    db.flush()

    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for line in payload.items:
        food_item = db.query(FoodItem).filter(FoodItem.id == line.food_item_id).first()
        if not food_item:
            raise HTTPException(status_code=404, detail=f"Food item {line.food_item_id} not found")
        amount = Decimal(str(food_item.price)) * line.quantity
        line_tax = amount * (Decimal(str(food_item.tax_percentage)) / 100)
        subtotal += amount
        tax_total += line_tax
        db.add(FoodOrderItem(
            order_id=order.id,
            food_item_id=food_item.id,
            quantity=line.quantity,
            unit_price=food_item.price,
            amount=amount,
        ))

    total_discount = apply_membership_discount(db, payload.customer_id, subtotal, payload.discount)
    order.subtotal = subtotal
    order.discount = total_discount
    order.tax = tax_total
    order.total_amount = calculate_grand_total(subtotal, tax_total, total_discount)
    notify_customer(db, payload.customer_id, "Order placed",
                     f"Your food order {order.order_code} has been placed.")
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=List[FoodOrderOut])
def list_food_orders(status_filter: Optional[OrderStatus] = None, customer_id: Optional[int] = None,
                      db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(FoodOrder)
    if status_filter:
        query = query.filter(FoodOrder.status == status_filter)
    if customer_id:
        query = query.filter(FoodOrder.customer_id == customer_id)
    return query.order_by(FoodOrder.id.desc()).all()


@router.get("/orders/{order_id}", response_model=FoodOrderOut)
def get_food_order(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}/status", response_model=FoodOrderOut)
def update_order_status(order_id: int, new_status: OrderStatus, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    """Kitchen/food-servant workflow: New -> Preparing -> Ready -> Served -> Completed (Section 57/58)."""
    order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = new_status
    if new_status == OrderStatus.READY:
        notify_customer(db, order.customer_id, "Order ready",
                         f"Your order {order.order_code} is ready to be served.")
    db.commit()
    db.refresh(order)
    return order
