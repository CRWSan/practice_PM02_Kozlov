"""
Abstractions (Port-Adapter pattern)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from ..core.domain import Booking, Room, BookingStatus


class IBookingRepository(ABC):
    """Repository interface for bookings"""
    
    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        """Save a booking"""
        pass
    
    @abstractmethod
    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        pass
    
    @abstractmethod
    def get_by_room_and_dates(self, room_id: int, check_in, check_out) -> List[Booking]:
        """Get bookings for a room in date range"""
        pass
    
    @abstractmethod
    def get_by_guest_email(self, email: str) -> List[Booking]:
        """Get bookings by guest email"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: BookingStatus) -> List[Booking]:
        """Get bookings by status"""
        pass
    
    @abstractmethod
    def delete(self, booking_id: str) -> None:
        """Delete a booking"""
        pass


class IRoomRepository(ABC):
    """Repository interface for rooms"""
    
    @abstractmethod
    def save(self, room: Room) -> Room:
        """Save a room"""
        pass
    
    @abstractmethod
    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Get room by ID"""
        pass
    
    @abstractmethod
    def get_by_hotel(self, hotel_id: int) -> List[Room]:
        """Get all rooms for a hotel"""
        pass


class IEventBus(ABC):
    """Event bus interface"""
    
    @abstractmethod
    def publish(self, event) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type, handler) -> None:
        """Subscribe to an event type"""
        pass


class IPaymentService(ABC):
    """Payment service interface"""
    
    @abstractmethod
    def process_payment(self, booking_id: str, amount: float) -> bool:
        """Process payment for a booking"""
        pass
    
    @abstractmethod
    def refund_payment(self, booking_id: str) -> bool:
        """Refund payment for a booking"""
        pass