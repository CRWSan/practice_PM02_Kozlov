"""
Test data factory
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from src.core.domain import Booking, BookingStatus, Money, Room
import uuid


class DataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_booking(
        room_id: int = 1,
        guest_name: str = "John Doe",
        guest_email: str = "john@example.com",
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        status: BookingStatus = BookingStatus.PENDING,
        price: float = 100.0,
        nights: int = 5
    ) -> Booking:
        """Create a test booking"""
        if check_in is None:
            check_in = date(2026, 6, 15)
        if check_out is None:
            check_out = check_in + timedelta(days=nights)
        
        return Booking(
            id=str(uuid.uuid4()),
            room_id=room_id,
            guest_name=guest_name,
            guest_email=guest_email,
            check_in=check_in,
            check_out=check_out,
            status=status,
            total_price=Money(price * nights, "USD"),
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_room(
        room_id: int = 1,
        hotel_id: int = 1,
        number: str = "101",
        room_type: str = "Standard",
        price: float = 100.0,
        capacity: int = 2,
        is_available: bool = True
    ) -> Room:
        """Create a test room"""
        return Room(
            id=room_id,
            hotel_id=hotel_id,
            number=number,
            room_type=room_type,
            price_per_night=Money(price, "USD"),
            capacity=capacity,
            is_available=is_available
        )
    
    @staticmethod
    def create_multiple_bookings(
        count: int,
        room_id: int = 1,
        start_date: Optional[date] = None
    ) -> List[Booking]:
        """Create multiple test bookings"""
        if start_date is None:
            start_date = date(2026, 6, 15)
        
        bookings = []
        for i in range(count):
            check_in = start_date + timedelta(days=i * 7)
            check_out = check_in + timedelta(days=3)
            
            booking = DataFactory.create_booking(
                room_id=room_id,
                guest_name=f"Guest {i+1}",
                guest_email=f"guest{i+1}@example.com",
                check_in=check_in,
                check_out=check_out
            )
            bookings.append(booking)
        
        return bookings
    
    @staticmethod
    def create_overlapping_bookings(
        room_id: int = 1,
        base_date: Optional[date] = None
    ) -> List[Booking]:
        """Create overlapping test bookings"""
        if base_date is None:
            base_date = date(2026, 6, 15)
        
        bookings = [
            DataFactory.create_booking(
                room_id=room_id,
                guest_name="Guest A",
                guest_email="a@example.com",
                check_in=base_date,
                check_out=base_date + timedelta(days=5),
                nights=5
            ),
            DataFactory.create_booking(
                room_id=room_id,
                guest_name="Guest B",
                guest_email="b@example.com",
                check_in=base_date + timedelta(days=3),
                check_out=base_date + timedelta(days=8),
                nights=5
            )
        ]
        
        return bookings