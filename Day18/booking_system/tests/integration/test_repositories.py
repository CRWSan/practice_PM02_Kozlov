"""
Integration tests for repositories
"""
import pytest
from datetime import date, datetime
from src.core.domain import Booking, BookingStatus, Money, Room
from src.infrastructure.repositories import InMemoryBookingRepository, InMemoryRoomRepository


class TestInMemoryBookingRepository:
    """Test InMemoryBookingRepository"""
    
    @pytest.fixture
    def repo(self):
        return InMemoryBookingRepository()
    
    def test_save_and_get_by_id(self, repo):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        
        repo.save(booking)
        found = repo.get_by_id("test-1")
        
        assert found is not None
        assert found.id == "test-1"
        assert found.guest_name == "John Doe"
    
    def test_get_by_room_and_dates(self, repo):
        # Create bookings
        booking1 = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        booking2 = Booking(
            id="test-2",
            room_id=1,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            check_in=date(2026, 6, 20),
            check_out=date(2026, 6, 25),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        booking3 = Booking(
            id="test-3",
            room_id=2,
            guest_name="Bob Smith",
            guest_email="bob@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        
        repo.save(booking1)
        repo.save(booking2)
        repo.save(booking3)
        
        # Get bookings for room 1 in date range
        bookings = repo.get_by_room_and_dates(
            1, date(2026, 6, 16), date(2026, 6, 18)
        )
        assert len(bookings) == 1
        assert bookings[0].id == "test-1"
    
    def test_get_by_guest_email(self, repo):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        repo.save(booking)
        
        bookings = repo.get_by_guest_email("john@example.com")
        assert len(bookings) == 1
        
        bookings = repo.get_by_guest_email("unknown@example.com")
        assert len(bookings) == 0
    
    def test_get_by_status(self, repo):
        booking1 = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        booking2 = Booking(
            id="test-2",
            room_id=1,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            check_in=date(2026, 6, 20),
            check_out=date(2026, 6, 25),
            status=BookingStatus.CONFIRMED,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        
        repo.save(booking1)
        repo.save(booking2)
        
        pending = repo.get_by_status(BookingStatus.PENDING)
        assert len(pending) == 1
        
        confirmed = repo.get_by_status(BookingStatus.CONFIRMED)
        assert len(confirmed) == 1
    
    def test_delete(self, repo):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        repo.save(booking)
        repo.delete("test-1")
        
        found = repo.get_by_id("test-1")
        assert found is None
    
    def test_clear(self, repo):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.PENDING,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        repo.save(booking)
        repo.clear()
        
        found = repo.get_by_id("test-1")
        assert found is None


class TestInMemoryRoomRepository:
    """Test InMemoryRoomRepository"""
    
    @pytest.fixture
    def repo(self):
        return InMemoryRoomRepository()
    
    def test_save_and_get_by_id(self, repo):
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2
        )
        
        repo.save(room)
        found = repo.get_by_id(1)
        
        assert found is not None
        assert found.number == "101"
        assert found.room_type == "Standard"
    
    def test_get_by_hotel(self, repo):
        room1 = Room(1, 1, "101", "Standard", Money(100, "USD"), 2)
        room2 = Room(2, 1, "102", "Deluxe", Money(200, "USD"), 2)
        room3 = Room(3, 2, "201", "Standard", Money(100, "USD"), 2)
        
        repo.save(room1)
        repo.save(room2)
        repo.save(room3)
        
        hotel1_rooms = repo.get_by_hotel(1)
        assert len(hotel1_rooms) == 2
        
        hotel2_rooms = repo.get_by_hotel(2)
        assert len(hotel2_rooms) == 1