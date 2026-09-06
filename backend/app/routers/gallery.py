from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])


class GalleryImageCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    title: Optional[str] = None
    image_url: str


class GalleryImageOut(GalleryImageCreate):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[GalleryImageOut])
def list_gallery(category: Optional[str] = None, db: Session = Depends(get_db)):
    from app.models.content import GalleryImage
    query = db.query(GalleryImage)
    if category:
        query = query.filter(GalleryImage.category == category)
    return query.order_by(GalleryImage.id.desc()).all()


@router.post("", response_model=GalleryImageOut)
def add_gallery_image(payload: GalleryImageCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    from app.models.content import GalleryImage
    image = GalleryImage(**payload.model_dump())
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
