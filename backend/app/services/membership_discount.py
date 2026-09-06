from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session


def get_active_membership_discount_percentage(db: Session, customer_id: int) -> Decimal:
    """Returns the customer's active membership discount percentage (Section 6: Membership
    Benefits include room/restaurant/club/spa/pool discounts), or 0 if none/expired.
    If a customer somehow holds more than one active membership, the highest discount wins.
    """
    from app.models.customer import Membership, MembershipPlan
    from app.models.enums import UserStatus

    today = date.today()
    rows = (
        db.query(MembershipPlan.discount_percentage)
        .join(Membership, Membership.plan_id == MembershipPlan.id)
        .filter(
            Membership.customer_id == customer_id,
            Membership.status == UserStatus.ACTIVE,
            Membership.start_date <= today,
            Membership.end_date >= today,
        )
        .all()
    )
    if not rows:
        return Decimal("0")
    return max(Decimal(str(r[0])) for r in rows)


def apply_membership_discount(db: Session, customer_id: int, subtotal, manual_discount=0) -> Decimal:
    """Combines an automatic membership discount (computed off subtotal) with any manual
    discount a staff member entered, returning the total discount amount to bill."""
    pct = get_active_membership_discount_percentage(db, customer_id)
    membership_discount = (Decimal(str(subtotal)) * pct / 100) if pct else Decimal("0")
    return membership_discount + Decimal(str(manual_discount or 0))
