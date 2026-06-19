import pytest
from datetime import date
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService
from src.domain.models import Hotel, Room, Booking, BookingStatus


@pytest.fixture
def uow():
    return UnitOfWork()


@pytest.fixture
def pricing_service():
    return PricingService()


@pytest.fixture
def booking_service(uow, pricing_service):
    return BookingService(uow, pricing_service)


@pytest.fixture
def sample_hotel():
    return Hotel(
        id=None,
        name="Test Hotel",
        address="123 Test St",
        phone="+1234567890",
        rating=4.5
    )


@pytest.fixture
def sample_room(sample_hotel, uow):
    hotel = uow.hotels.add(sample_hotel)
    room = Room(
        id=None,
        hotel_id=hotel.id,
        number="101",
        capacity=2,
        price_per_night=100.0,
        is_active=True
    )
    return uow.rooms.add(room)


@pytest.fixture
def sample_booking(sample_room, uow):
    booking = Booking(
        id=None,
        room_id=sample_room.id,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20),
        total_price=500.0,
        status=BookingStatus.PENDING
    )
    return uow.bookings.add(booking)