from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.content import Offer, TravelStory, InfoPage

router = APIRouter(prefix="/api/content", tags=["Content"])


class OfferCreate(BaseModel):
    title: str
    description: Optional[str] = None
    discount_percentage: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class OfferOut(OfferCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class TravelStoryCreate(BaseModel):
    title: str
    content: str
    cover_image_url: Optional[str] = None


class TravelStoryOut(TravelStoryCreate):
    id: int
    published_at: datetime
    is_published: bool

    class Config:
        from_attributes = True


@router.get("/offers", response_model=List[OfferOut])
def list_offers(db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.is_active == True).all()  # noqa: E712


@router.post("/offers", response_model=OfferOut)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    offer = Offer(**payload.model_dump(), is_active=True)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.get("/travel-stories", response_model=List[TravelStoryOut])
def list_travel_stories(db: Session = Depends(get_db)):
    return db.query(TravelStory).filter(TravelStory.is_published == True).order_by(  # noqa: E712
        TravelStory.published_at.desc()
    ).all()


@router.post("/travel-stories", response_model=TravelStoryOut)
def create_travel_story(payload: TravelStoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    story = TravelStory(**payload.model_dump(), is_published=True)
    db.add(story)
    db.commit()
    db.refresh(story)
    return story


# ---------- Info Pages (More menu: Dining, Meetings & Conferences, Weddings, Holiday Stays,
# Safaris, Wellness, Gifting, Business Users, About Hotel, Sky View Residences) ----------

class InfoPageCreate(BaseModel):
    slug: str
    title: str
    tagline: Optional[str] = None
    content: Optional[str] = None
    cta_label: Optional[str] = None
    cta_target: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class InfoPageOut(InfoPageCreate):
    id: int
    is_published: bool

    class Config:
        from_attributes = True


@router.get("/info-pages", response_model=List[InfoPageOut])
def list_info_pages(db: Session = Depends(get_db)):
    return db.query(InfoPage).filter(InfoPage.is_published == True).order_by(  # noqa: E712
        InfoPage.display_order
    ).all()


@router.get("/info-pages/{slug}", response_model=InfoPageOut)
def get_info_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(InfoPage).filter(InfoPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.post("/info-pages", response_model=InfoPageOut)
def create_info_page(payload: InfoPageCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(InfoPage).filter(InfoPage.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="A page with this slug already exists")
    page = InfoPage(**payload.model_dump(), is_published=True)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.put("/info-pages/{slug}", response_model=InfoPageOut)
def update_info_page(slug: str, payload: InfoPageCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    page = db.query(InfoPage).filter(InfoPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    for field, value in payload.model_dump().items():
        setattr(page, field, value)
    db.commit()
    db.refresh(page)
    return page
