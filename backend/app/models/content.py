from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import EnquiryStatus


class GalleryImage(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # hotel/restaurant/rooms/party_hall/pool/spa
    subcategory = Column(String(100), nullable=True)  # exterior/interior/wedding_setup/etc.
    title = Column(String(150), nullable=True)
    image_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ContactEnquiry(Base):
    __tablename__ = "contact_enquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SAEnum(EnquiryStatus), default=EnquiryStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    discount_percentage = Column(String(10), nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class TravelStory(Base):
    __tablename__ = "travel_stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    cover_image_url = Column(String(500), nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    channel = Column(String(20), default="in_app")  # email/sms/whatsapp/in_app
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    employee = relationship("Employee")


class InfoPage(Base):
    """Admin-managed content for the 'More' menu's static-ish sections (Section 38-49:
    Dining, Meetings & Conferences, Timeless Weddings, Holiday Stays, Hotel Safaris,
    Hotel Wellness, Gifting, Business Users, About Hotel, Sky View Residences) — so these
    are editable content, not text hardcoded into the frontend."""
    __tablename__ = "info_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    tagline = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    cta_label = Column(String(50), nullable=True)
    cta_target = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
