"""
Domain models: Aggregates, Entities, Value Objects
"""
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
import uuid


class BookingStatus(Enum):
    """Status of a booking"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PaymentStatus(Enum):
    """Status of a payment"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Address:
    """Value Object for address"""
    street: str
    city: str
    country: str
    postal_code: str
    
    def __post_init__(self):
        if not self.street or not self.city:
            raise ValueError("Street and city are required")


@dataclass
class Money:
    """Value Object for money"""
    amount: float
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self.amount * factor, self.currency)


@dataclass
class Booking:
    """Booking aggregate root"""
    id: str
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    status: BookingStatus
    total_price: Money
    created_at: datetime
    updated_at: Optional[datetime] = None
    guest_phone: Optional[str] = None
    
    def __post_init__(self):
        if self.check_in >= self.check_out:
            raise ValueError("Check-in must be before check-out")
        if self.total_price.amount <= 0:
            raise ValueError("Total price must be positive")
        if not self.guest_email or '@' not in self.guest_email:
            raise ValueError("Invalid email")
    
    def cancel(self) -> 'Booking':
        """Cancel the booking"""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Booking already cancelled")
        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Cannot cancel completed booking")
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()
        return self
    
    def confirm(self) -> 'Booking':
        """Confirm the booking"""
        if self.status != BookingStatus.PENDING:
            raise ValueError("Only pending bookings can be confirmed")
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now()
        return self
    
    def complete(self) -> 'Booking':
        """Complete the booking"""
        if self.status not in [BookingStatus.CONFIRMED]:
            raise ValueError("Only confirmed bookings can be completed")
        self.status = BookingStatus.COMPLETED
        self.updated_at = datetime.now()
        return self
    
    def get_nights_count(self) -> int:
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days


@dataclass
class Room:
    """Room entity"""
    id: int
    hotel_id: int
    number: str
    room_type: str
    price_per_night: Money
    capacity: int
    is_available: bool = True
    amenities: List[str] = None
    
    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError("Capacity must be positive")
        if self.price_per_night.amount <= 0:
            raise ValueError("Price must be positive")
        if not self.room_type:
            raise ValueError("Room type is required")
        if self.amenities is None:
            self.amenities = []
    
    def book(self) -> None:
        """Mark room as booked"""
        if not self.is_available:
            raise ValueError("Room is not available")
        self.is_available = False
    
    def release(self) -> None:
        """Release room"""
        self.is_available = True


@dataclass
class Hotel:
    """Hotel aggregate"""
    id: int
    name: str
    address: Address
    rating: float
    rooms: List[Room]
    description: str = ""
    
    def __post_init__(self):
        if self.rating < 0 or self.rating > 5:
            raise ValueError("Rating must be between 0 and 5")
        if not self.name:
            raise ValueError("Hotel name is required")
    
    def get_available_rooms(self) -> List[Room]:
        """Get all available rooms"""
        return [room for room in self.rooms if room.is_available]
    
    def get_room_by_number(self, room_number: str) -> Optional[Room]:
        """Find room by room number"""
        for room in self.rooms:
            if room.number == room_number:
                return room
        return None
    
    def get_rooms_by_type(self, room_type: str) -> List[Room]:
        """Get rooms by type"""
        return [room for room in self.rooms if room.room_type == room_type]