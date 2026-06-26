"""
Unit tests for services
"""
import pytest
from datetime import date, datetime
from src.core.domain import Booking, BookingStatus, Money, Room
from src.core.exceptions import BookingNotFoundError, RoomNotAvailableError
from src.application.services import BookingService, HotelService
from src.application.dto import BookingCreateDTO
from src.infrastructure.repositories import InMemoryBookingRepository, InMemoryRoomRepository


class TestBookingService:
    """Test BookingService"""
    
    @pytest.fixture
    def service(self):
        booking_repo = InMemoryBookingRepository()
        room_repo = InMemoryRoomRepository()
        
        # Add a test room
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2
        )
        room_repo.save(room)
        
        return BookingService(booking_repo, room_repo)
    
    def test_create_booking(self, service):
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        
        booking = service.create_booking(dto)
        
        assert booking.id is not None
        assert booking.room_id == 1
        assert booking.guest_name == "John Doe"
        assert booking.status == BookingStatus.PENDING
        assert booking.total_price.amount == 500.0  # 5 nights * $100
    
    def test_create_booking_invalid_dates(self, service):
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 20),
            check_out=date(2026, 6, 15),
            guest_phone="+1234567890"
        )
        
        with pytest.raises(Exception, match="Check-in must be before check-out"):
            service.create_booking(dto)
    
    def test_create_booking_room_not_available(self, service):
        # First booking
        dto1 = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        service.create_booking(dto1)
        
        # Second booking overlapping
        dto2 = BookingCreateDTO(
            room_id=1,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            check_in=date(2026, 6, 16),
            check_out=date(2026, 6, 18),
            guest_phone="+0987654321"
        )
        
        with pytest.raises(RoomNotAvailableError):
            service.create_booking(dto2)
    
    def test_cancel_booking(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        booking = service.create_booking(dto)
        
        # Cancel booking
        cancelled = service.cancel_booking(booking.id)
        
        assert cancelled.status == BookingStatus.CANCELLED
    
    def test_cancel_booking_not_found(self, service):
        with pytest.raises(BookingNotFoundError):
            service.cancel_booking("non-existent-id")
    
    def test_cancel_booking_changes_status(self, service):
        """Test that canceling changes status (FIXED)"""
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        booking = service.create_booking(dto)
        
        # Verify it's PENDING
        assert booking.status == BookingStatus.PENDING
        
        # Cancel
        cancelled = service.cancel_booking(booking.id)
        
        # FIXED: Now it should be CANCELLED, not deleted
        assert cancelled.status == BookingStatus.CANCELLED
        
        # Verify we can still find it
        found = service.get_booking(booking.id)
        assert found is not None
        assert found.status == BookingStatus.CANCELLED
    
    def test_cancelled_booking_doesnt_block_room(self, service):
        """Test that cancelled bookings don't block room (FIXED)"""
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        booking = service.create_booking(dto)
        
        # Cancel it
        service.cancel_booking(booking.id)
        
        # Check availability - should be available
        available = service.is_room_available(1, date(2026, 6, 16), date(2026, 6, 18))
        
        # FIXED: Should return True because cancelled booking doesn't block
        assert available is True
    
    def test_cancel_nonexistent_booking(self, service):
        with pytest.raises(BookingNotFoundError):
            service.cancel_booking("999")
    
    def test_confirm_booking(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        booking = service.create_booking(dto)
        
        # Confirm
        confirmed = service.confirm_booking(booking.id)
        
        assert confirmed.status == BookingStatus.CONFIRMED
    
    def test_get_booking(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        booking = service.create_booking(dto)
        
        # Get booking
        found = service.get_booking(booking.id)
        assert found is not None
        assert found.id == booking.id
    
    def test_get_bookings_by_email(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        service.create_booking(dto)
        
        # Get by email
        bookings = service.get_bookings_by_email("john@example.com")
        assert len(bookings) == 1
    
    def test_is_room_available_different_room(self, service):
        # No bookings for room 2
        available = service.is_room_available(2, date(2026, 6, 15), date(2026, 6, 20))
        assert available is True
    
    def test_is_room_available_no_overlap(self, service):
        # Create booking for one date range
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        service.create_booking(dto)
        
        # Check non-overlapping dates
        available = service.is_room_available(1, date(2026, 6, 20), date(2026, 6, 25))
        assert available is True
    
    def test_is_room_available_exact_check_in(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        service.create_booking(dto)
        
        # Check availability for same check-in date
        available = service.is_room_available(1, date(2026, 6, 15), date(2026, 6, 18))
        assert available is False
    
    def test_is_room_available_exact_check_out(self, service):
        # Create booking
        dto = BookingCreateDTO(
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            guest_phone="+1234567890"
        )
        service.create_booking(dto)
        
        # Check availability starting on check-out date
        available = service.is_room_available(1, date(2026, 6, 20), date(2026, 6, 25))
        assert available is True  # Can check in on check-out day


class TestHotelService:
    """Test HotelService"""
    
    @pytest.fixture
    def service(self):
        room_repo = InMemoryRoomRepository()
        
        # Add test rooms
        room1 = Room(1, 1, "101", "Standard", Money(100, "USD"), 2, True)
        room2 = Room(2, 1, "102", "Deluxe", Money(200, "USD"), 2, False)
        room3 = Room(3, 1, "103", "Suite", Money(300, "USD"), 4, True)
        room_repo.save(room1)
        room_repo.save(room2)
        room_repo.save(room3)
        
        return HotelService(room_repo)
    
    def test_search_rooms(self, service):
        rooms = service.search_rooms(
            1, 
            date(2026, 6, 15), 
            date(2026, 6, 20)
        )
        assert len(rooms) == 2  # room1 and room3 are available
        assert all(room.is_available for room in rooms)
    
    def test_search_rooms_with_capacity_filter(self, service):
        rooms = service.search_rooms(
            1,
            date(2026, 6, 15),
            date(2026, 6, 20),
            capacity=3
        )
        assert len(rooms) == 1
        assert rooms[0].capacity >= 3