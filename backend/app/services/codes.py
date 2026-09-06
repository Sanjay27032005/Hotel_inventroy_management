from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session


def _next_sequence(db: Session, model, code_column, prefix: str) -> str:
    """Generate the next sequential code like BK-2026-000001, scoped per calendar year."""
    year = datetime.utcnow().year
    year_prefix = f"{prefix}-{year}-"
    count = (
        db.query(func.count())
        .select_from(model)
        .filter(code_column.like(f"{year_prefix}%"))
        .scalar()
    ) or 0
    next_number = count + 1
    return f"{year_prefix}{next_number:06d}"


def generate_booking_code(db: Session) -> str:
    from app.models.booking_billing import Booking
    return _next_sequence(db, Booking, Booking.booking_code, "BK")


def generate_sub_booking_code(db: Session, model, code_column, prefix: str) -> str:
    return _next_sequence(db, model, code_column, prefix)


def generate_invoice_number(db: Session) -> str:
    from app.models.booking_billing import Invoice
    return _next_sequence(db, Invoice, Invoice.invoice_number, "INV")


def generate_payment_code(db: Session) -> str:
    from app.models.booking_billing import Payment
    return _next_sequence(db, Payment, Payment.payment_code, "PAY")


def generate_employee_code(db: Session) -> str:
    from app.models.core import Employee
    return _next_sequence(db, Employee, Employee.employee_code, "EMP")


def generate_customer_code(db: Session) -> str:
    from app.models.customer import Customer
    return _next_sequence(db, Customer, Customer.customer_code, "CUS")


def generate_membership_code(db: Session) -> str:
    from app.models.customer import Membership
    return _next_sequence(db, Membership, Membership.membership_code, "MEM")


def money(value) -> Decimal:
    """Round to 2 decimal places using standard rounding — used everywhere a bill is totalled."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_grand_total(subtotal, tax=0, discount=0, additional_charges=0) -> Decimal:
    """Grand Total = Subtotal + Tax - Discount + Additional Charges (per doc Section 14/40)."""
    return money(
        money(subtotal) + money(tax) - money(discount) + money(additional_charges)
    )
