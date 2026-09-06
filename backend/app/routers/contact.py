from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_staff_any
from app.models.content import ContactEnquiry
from app.models.enums import EnquiryStatus

router = APIRouter(prefix="/api/contact", tags=["Contact"])


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str


class ContactOut(ContactCreate):
    id: int
    status: EnquiryStatus
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=ContactOut)
def submit_enquiry(payload: ContactCreate, db: Session = Depends(get_db)):
    enquiry = ContactEnquiry(**payload.model_dump(), status=EnquiryStatus.NEW)
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry


@router.get("", response_model=List[ContactOut])
def list_enquiries(status_filter: Optional[EnquiryStatus] = None, db: Session = Depends(get_db),
                    _=Depends(require_staff_any)):
    query = db.query(ContactEnquiry)
    if status_filter:
        query = query.filter(ContactEnquiry.status == status_filter)
    return query.order_by(ContactEnquiry.id.desc()).all()


@router.put("/{enquiry_id}/status", response_model=ContactOut)
def update_enquiry_status(enquiry_id: int, new_status: EnquiryStatus, db: Session = Depends(get_db),
                           _=Depends(require_staff_any)):
    enquiry = db.query(ContactEnquiry).filter(ContactEnquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.status = new_status
    db.commit()
    db.refresh(enquiry)
    return enquiry
