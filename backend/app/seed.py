"""
Seeds master/reference data so the application is usable immediately after setup:
departments, room types, food categories & sample items, event types, spa services,
laundry cloth prices, pool package prices, membership plans, a sample hotel/location,
and a sample restaurant table + room.

Run with:  python -m app.seed
"""
from app.core.database import SessionLocal, Base, engine
import app.models  # noqa: F401
from app.models.core import Department
from app.models.location import Country, StateModel, City, Hotel
from app.models.accommodation import RoomType, Room
from app.models.restaurant import FoodCategory, FoodItem, RestaurantTable
from app.models.events import EventType, PartyHall
from app.models.pool import PoolPackagePrice, Trainer
from app.models.spa import SpaService, Therapist
from app.models.club import ClubFoodItem, ClubDrinkItem
from app.models.laundry import LaundryServicePrice
from app.models.customer import MembershipPlan
from app.models.content import InfoPage
from app.models.enums import RoomCustomerCategory, PoolCustomerType, PoolPackageType


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Department).first():
            for name in ["Management", "Reception", "Housekeeping", "Restaurant", "Kitchen",
                         "Billing / Accounts", "Events", "Spa", "Swimming Pool", "Club & Bar",
                         "Laundry", "Security", "Maintenance"]:
                db.add(Department(name=name))

        if not db.query(Country).first():
            india = Country(name="India")
            db.add(india)
            db.flush()
            tn = StateModel(name="Tamil Nadu", country_id=india.id)
            db.add(tn)
            db.flush()
            chennai = City(name="Chennai", state_id=tn.id)
            pondy = City(name="Puducherry", state_id=tn.id)
            db.add_all([chennai, pondy])
            db.flush()
            db.add(Hotel(
                name="CoreStone Grand Hotel", address="ECR Road, Puducherry",
                phone="+91-9000000000", email="reservations@corestone-hrm.com",
                city_id=pondy.id, description="Flagship property for the Hotel & Restaurant Management System demo.",
            ))

        if not db.query(RoomType).first():
            room_types = [
                RoomType(name="Standard Single Room", customer_category=RoomCustomerCategory.SINGLE,
                          hourly_rate=300, daily_rate=2000, weekly_rate=12000, monthly_rate=45000,
                          max_adults=1, max_children=0),
                RoomType(name="Standard Twin Room - 2 Beds", customer_category=RoomCustomerCategory.FAMILY,
                          hourly_rate=400, daily_rate=2800, weekly_rate=17000, monthly_rate=60000,
                          max_adults=2, max_children=2),
                RoomType(name="Standard Double Room", customer_category=RoomCustomerCategory.COUPLE,
                          hourly_rate=400, daily_rate=3000, weekly_rate=18000, monthly_rate=65000,
                          max_adults=2, max_children=1),
                RoomType(name="Superior Double Room", customer_category=RoomCustomerCategory.COUPLE,
                          hourly_rate=550, daily_rate=4200, weekly_rate=25000, monthly_rate=90000,
                          max_adults=2, max_children=1),
                RoomType(name="Superior Twin Room - 2 Beds", customer_category=RoomCustomerCategory.FAMILY,
                          hourly_rate=600, daily_rate=4600, weekly_rate=27000, monthly_rate=95000,
                          max_adults=3, max_children=2),
            ]
            db.add_all(room_types)
            db.flush()
            db.add_all([
                Room(room_number="101", room_type_id=room_types[0].id, floor="1"),
                Room(room_number="102", room_type_id=room_types[1].id, floor="1"),
                Room(room_number="201", room_type_id=room_types[2].id, floor="2"),
                Room(room_number="202", room_type_id=room_types[3].id, floor="2"),
                Room(room_number="301", room_type_id=room_types[4].id, floor="3"),
            ])

        if not db.query(RestaurantTable).first():
            for i in range(1, 9):
                db.add(RestaurantTable(table_number=f"T{i:02d}", capacity=4 if i % 2 else 2,
                                        table_type="indoor" if i <= 6 else "outdoor"))

        if not db.query(FoodCategory).first():
            categories = {}
            for name, meal in [
                ("Indian", "dinner"), ("Traditional", "lunch"), ("Soups", "dinner"),
                ("Biriyani", "lunch"), ("Idli", "breakfast"), ("Dosa", "breakfast"),
                ("Starters", "evening"), ("Main Course", "dinner"), ("Desserts", "dinner"),
                ("Beverages", "evening"), ("Other Food Items", "lunch"),
            ]:
                cat = FoodCategory(name=name, meal_category=meal)
                db.add(cat)
                db.flush()
                categories[name] = cat.id
            db.add_all([
                FoodItem(name="Masala Dosa", category_id=categories["Dosa"], price=90, tax_percentage=5),
                FoodItem(name="Idli Sambar (4 pcs)", category_id=categories["Idli"], price=70, tax_percentage=5),
                FoodItem(name="Chicken Biriyani", category_id=categories["Biriyani"], price=250, tax_percentage=5),
                FoodItem(name="Veg Biriyani", category_id=categories["Biriyani"], price=180, tax_percentage=5),
                FoodItem(name="Tomato Soup", category_id=categories["Soups"], price=110, tax_percentage=5),
                FoodItem(name="Paneer Butter Masala", category_id=categories["Main Course"], price=220, tax_percentage=5),
                FoodItem(name="Gulab Jamun (2 pcs)", category_id=categories["Desserts"], price=80, tax_percentage=5),
                FoodItem(name="Filter Coffee", category_id=categories["Beverages"], price=40, tax_percentage=5),
            ])

        if not db.query(EventType).first():
            for name in ["Birthday", "Wedding Ceremony", "Office Party", "Meetings & Events",
                         "Event Programmes", "Other Events"]:
                db.add(EventType(name=name))
            db.add(PartyHall(name="Grand Ballroom", capacity=300, location="Ground Floor",
                              facilities="Stage, Sound system, AC, Parking",
                              hourly_rate=5000, daily_rate=35000, weekly_rate=200000))
            db.add(PartyHall(name="Conference Room A", capacity=40, location="1st Floor",
                              facilities="Projector, Whiteboard, AC, Wi-Fi",
                              hourly_rate=1500, daily_rate=9000, weekly_rate=50000))

        if not db.query(PoolPackagePrice).first():
            prices = {
                (PoolCustomerType.CHILD, PoolPackageType.HOURLY): 150,
                (PoolCustomerType.CHILD, PoolPackageType.MONTHLY): 2000,
                (PoolCustomerType.CHILD, PoolPackageType.TRAINER): 3000,
                (PoolCustomerType.ADULT, PoolPackageType.HOURLY): 250,
                (PoolCustomerType.ADULT, PoolPackageType.MONTHLY): 3500,
                (PoolCustomerType.ADULT, PoolPackageType.TRAINER): 5000,
                (PoolCustomerType.COUPLE, PoolPackageType.HOURLY): 400,
                (PoolCustomerType.COUPLE, PoolPackageType.MONTHLY): 6000,
                (PoolCustomerType.COUPLE, PoolPackageType.TRAINER): 8500,
            }
            for (ct, pt), price in prices.items():
                db.add(PoolPackagePrice(customer_type=ct, package_type=pt, price=price))
            db.add(Trainer(name="Arun Kumar", specialization="Swimming coach"))

        if not db.query(SpaService).first():
            db.add_all([
                SpaService(name="Traditional Massage", service_price=1500, hourly_rate=1500),
                SpaService(name="Thai Massage", service_price=1800, hourly_rate=1800),
                SpaService(name="Foot Reflexology", service_price=900, hourly_rate=900),
                SpaService(name="Hot Stone Therapy", service_price=2200, hourly_rate=2200),
            ])
            db.add(Therapist(name="Priya S", specialization="Thai & Traditional Massage"))

        if not db.query(ClubFoodItem).first():
            db.add_all([
                ClubFoodItem(name="Grilled Chicken Platter", unit_price=350),
                ClubFoodItem(name="Nachos", unit_price=180),
            ])
            db.add_all([
                ClubDrinkItem(name="Mocktail", unit_price=150),
                ClubDrinkItem(name="Draft Beer", unit_price=220),
            ])

        if not db.query(LaundryServicePrice).first():
            for cloth, price in [("Shirt", 40), ("Pant", 50), ("T-Shirt", 35), ("Suit", 150),
                                  ("Saree", 100), ("Jacket", 120), ("Other", 45)]:
                db.add(LaundryServicePrice(cloth_type=cloth, unit_price=price))

        if not db.query(MembershipPlan).first():
            db.add_all([
                MembershipPlan(name="Silver", fee=2000, duration_months=12, discount_percentage=5,
                                benefits="5% off restaurant and spa"),
                MembershipPlan(name="Gold", fee=5000, duration_months=12, discount_percentage=10,
                                benefits="10% off rooms, restaurant, spa and pool"),
                MembershipPlan(name="Platinum", fee=10000, duration_months=12, discount_percentage=15,
                                benefits="15% off all services plus complimentary events access"),
            ])

        if not db.query(InfoPage).first():
            info_pages = [
                ("dining", "Dining", "Restaurant, menu, dining experiences and table booking.", "Book a Table", 1),
                ("meetings-conferences", "Meetings & Conferences", "Conference rooms, corporate meetings, seminars and catering.", "Enquire Now", 2),
                ("timeless-weddings", "Timeless Weddings", "Wedding hall, decoration, catering and guest rooms.", "Plan Your Wedding", 3),
                ("holiday-stays", "Holiday Stays", "Family, couple, weekend and long-stay packages.", "Book Your Stay", 4),
                ("hotel-safaris", "Hotel Safaris", "Safari packages, destinations and transportation.", "Enquire", 5),
                ("hotel-wellness", "Hotel Wellness", "Spa, massage, pool and relaxation packages.", "Explore Wellness", 6),
                ("gifting", "Gifting", "Dining, spa, room-stay and membership vouchers.", "Enquire", 7),
                ("business-users", "Business Users", "Corporate room and meeting-room booking, bulk and corporate billing.", "Enquire", 8),
                ("about-hotel", "About Hotel", "Our introduction, history, vision, mission and facilities.", "Learn More", 9),
                ("sky-view-residences", "Sky View Residences", "Residence types, amenities and availability.", "Enquire", 10),
            ]
            for slug, title, tagline, cta_label, order in info_pages:
                db.add(InfoPage(slug=slug, title=title, tagline=tagline, content=tagline,
                                 cta_label=cta_label, display_order=order, is_published=True))

        db.commit()
        print("Seed data loaded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
