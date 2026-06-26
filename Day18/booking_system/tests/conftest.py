# tests/conftest.py
"""
Pytest configuration and fixtures
"""
import sys
import os
from datetime import date, datetime
import pytest

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now imports from src will work
from src.core.domain import Booking, BookingStatus, Money, Room
from src.application.services import BookingService
from src.infrastructure.repositories import InMemoryBookingRepository, InMemoryRoomRepository


@pytest.fixture
def booking_repo():
    """In-memory booking repository fixture"""
    return InMemoryBookingRepository()


@pytest.fixture
def room_repo():
    """In-memory room repository fixture"""
    repo = InMemoryRoomRepository()
    # Add a default room
    room = Room(
        id=1,
        hotel_id=1,
        number="101",
        room_type="Standard",
        price_per_night=Money(100.0, "USD"),
        capacity=2,
        is_available=True
    )
    repo.save(room)
    return repo


@pytest.fixture
def booking_service(booking_repo, room_repo):
    """Booking service fixture"""
    return BookingService(booking_repo, room_repo)


@pytest.fixture
def sample_booking():
    """Sample booking fixture"""
    return Booking(
        id="test-123",
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20),
        status=BookingStatus.PENDING,
        total_price=Money(500.0, "USD"),
        created_at=datetime.now()
    )


@pytest.fixture
def sample_room():
    """Sample room fixture"""
    return Room(
        id=1,
        hotel_id=1,
        number="101",
        room_type="Standard",
        price_per_night=Money(100.0, "USD"),
        capacity=2,
        is_available=True
    )