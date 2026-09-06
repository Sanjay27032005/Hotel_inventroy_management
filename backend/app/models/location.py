from sqlalchemy import Column, Integer, String, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    states = relationship("StateModel", back_populates="country")


class StateModel(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)

    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state")


class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)

    state = relationship("StateModel", back_populates="cities")
    hotels = relationship("Hotel", back_populates="city")


class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    map_location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)

    city = relationship("City", back_populates="hotels")
    images = relationship("HotelImage", back_populates="hotel")


class HotelImage(Base):
    __tablename__ = "hotel_images"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    category = Column(String(50), nullable=True)  # exterior/interior/etc

    hotel = relationship("Hotel", back_populates="images")
