from sqlalchemy.orm import Session


def notify_customer(db: Session, customer_id: int, title: str, message: str, channel: str = "in_app"):
    """Queues a notification row for the given customer. Does not commit — caller commits
    as part of the same transaction as the booking/payment it relates to, so the two never
    get out of sync."""
    if not customer_id:
        return
    from app.models.content import Notification
    db.add(Notification(customer_id=customer_id, channel=channel, title=title, message=message))


def notify_employee(db: Session, employee_id: int, title: str, message: str, channel: str = "in_app"):
    if not employee_id:
        return
    from app.models.content import Notification
    db.add(Notification(employee_id=employee_id, channel=channel, title=title, message=message))
