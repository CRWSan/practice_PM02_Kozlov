"""
Data Transfer Objects
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional, List
from ..core.domain import BookingStatus


@dataclass
class BookingCreateDTO:
    """DTO for creating a booking"""
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    guest_phone: Optional[str] = None


@dataclass
class BookingUpdateDTO:
    """DTO for updating a booking"""
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


@dataclass
class BookingResponseDTO:
    """DTO for booking response"""
    id: str
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    status: str
    total_price: float
    currency: str
    nights: int
    created_at: str


@dataclass
class RoomSearchDTO:
    """DTO for room search"""
    hotel_id: int
    check_in: date
    check_out: date
    capacity: Optional[int] = None
    room_type: Optional[str] = None


@dataclass
class PaymentDTO:
    """DTO for payment"""
    booking_id: str
    amount: float
    currency: str = "USD"
    payment_method: str = "credit_card"