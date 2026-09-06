from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.location import Country, StateModel, City, Hotel, HotelImage

router = APIRouter(prefix="/api/destinations", tags=["Destinations"])


class CountryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StateOut(BaseModel):
    id: int
    name: str
    country_id: int

    class Config:
        from_attributes = True


class CityOut(BaseModel):
    id: int
    name: str
    state_id: int

    class Config:
        from_attributes = True


class HotelCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    map_location: Optional[str] = None
    description: Optional[str] = None
    city_id: int


class HotelOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    map_location: Optional[str] = None
    description: Optional[str] = None
    city_id: int

    class Config:
        from_attributes = True


# --- Public browse endpoints (customer website) ---

@router.get("/countries", response_model=List[CountryOut])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()


@router.get("/countries/{country_id}/states", response_model=List[StateOut])
def list_states(country_id: int, db: Session = Depends(get_db)):
    return db.query(StateModel).filter(StateModel.country_id == country_id).all()


@router.get("/states/{state_id}/cities", response_model=List[CityOut])
def list_cities(state_id: int, db: Session = Depends(get_db)):
    return db.query(City).filter(City.state_id == state_id).all()


@router.get("/hotels", response_model=List[HotelOut])
def list_hotels(city_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Hotel)
    if city_id:
        query = query.filter(Hotel.city_id == city_id)
    return query.all()


@router.get("/hotels/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


# --- Admin management endpoints ---

@router.post("/countries", response_model=CountryOut)
def create_country(name: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    country = Country(name=name)
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


@router.post("/states", response_model=StateOut)
def create_state(name: str, country_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    state = StateModel(name=name, country_id=country_id)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


@router.post("/cities", response_model=CityOut)
def create_city(name: str, state_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    city = City(name=name, state_id=state_id)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.post("/hotels", response_model=HotelOut)
def create_hotel(payload: HotelCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    hotel = Hotel(**payload.model_dump())
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel
