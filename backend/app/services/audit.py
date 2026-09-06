from typing import Optional

from sqlalchemy.orm import Session


def log_action(db: Session, user, action: str, details: Optional[str] = None, ip_address: Optional[str] = None):
    """Queues an audit log entry. Does not commit — caller commits as part of the same
    transaction as the action it's recording."""
    from app.models.core import AuditLog
    db.add(AuditLog(
        user_id=user.id if user else None,
        action=action,
        details=details,
        ip_address=ip_address,
    ))
