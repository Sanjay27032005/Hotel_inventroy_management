import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    GENERAL_MANAGER = "general_manager"
    MANAGER = "manager"
    BILLING_PERSON = "billing_person"
    ROOM_SERVANT = "room_servant"
    FOOD_SERVANT = "food_servant"
    CHEF = "chef"
    CUSTOMER = "customer"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TableStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"


class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    UNDER_CLEANING = "under_cleaning"
    UNDER_MAINTENANCE = "under_maintenance"


class RateType(str, enum.Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RoomCustomerCategory(str, enum.Enum):
    SINGLE = "single"
    COUPLE = "couple"
    FAMILY = "family"


class BookingType(str, enum.Enum):
    DINING_TABLE = "dining_table"
    ROOM = "room"
    SPA_SESSION = "spa_session"
    EVENT = "event"
    SWIMMING_POOL = "swimming_pool"
    CLUB = "club"
    LAUNDRY = "laundry"
    STAY_REQUEST = "stay_request"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    ONLINE = "online"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PoolCustomerType(str, enum.Enum):
    CHILD = "child"
    ADULT = "adult"
    COUPLE = "couple"


class PoolPackageType(str, enum.Enum):
    HOURLY = "hourly"
    MONTHLY = "monthly"
    TRAINER = "trainer"


class LaundryPricingMethod(str, enum.Enum):
    CLOTH_BASED = "cloth_based"
    QUANTITY_BASED = "quantity_based"


class LaundryStatus(str, enum.Enum):
    RECEIVED = "received"
    WASHING = "washing"
    DRYING = "drying"
    IRONING = "ironing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class InvoiceServiceType(str, enum.Enum):
    RESTAURANT = "restaurant"
    ACCOMMODATION = "accommodation"
    PARTY_HALL = "party_hall"
    SWIMMING_POOL = "swimming_pool"
    SPA = "spa"
    CLUB_BAR = "club_bar"
    LAUNDRY = "laundry"


class EnquiryStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
