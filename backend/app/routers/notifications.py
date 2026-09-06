from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_staff_any
from app.models.content import Notification
from app.models.core import User

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class NotificationCreate(BaseModel):
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None
    channel: str = "in_app"
    title: str
    message: str


class NotificationOut(NotificationCreate):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=NotificationOut)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db), _=Depends(require_staff_any)):
    notif = Notification(**payload.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.get("/me", response_model=List[NotificationOut])
def my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Notification)
    if current_user.customer:
        query = query.filter(Notification.customer_id == current_user.customer.id)
    elif current_user.employee:
        query = query.filter(Notification.employee_id == current_user.employee.id)
    else:
        return []
    return query.order_by(Notification.created_at.desc()).all()


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
