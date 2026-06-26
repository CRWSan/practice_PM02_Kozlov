"""
Unit tests for domain models
"""
import pytest
from datetime import date, datetime
from src.core.domain import (
    Booking, BookingStatus, Money, Room, Hotel, Address,
    PaymentStatus
)


class TestMoney:
    """Test Money value object"""
    
    def test_create_money(self):
        money = Money(100.0, "USD")
        assert money.amount == 100.0
        assert money.currency == "USD"
    
    def test_money_negative_amount_raises_error(self):
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(-10.0, "USD")
    
    def test_money_add(self):
        m1 = Money(100.0, "USD")
        m2 = Money(50.0, "USD")
        result = m1.add(m2)
        assert result.amount == 150.0
        assert result.currency == "USD"
    
    def test_money_add_different_currency_raises_error(self):
        m1 = Money(100.0, "USD")
        m2 = Money(50.0, "EUR")
        with pytest.raises(ValueError, match="Cannot add different currencies"):
            m1.add(m2)
    
    def test_money_multiply(self):
        money = Money(100.0, "USD")
        result = money.multiply(1.5)
        assert result.amount == 150.0
        assert result.currency == "USD"


class TestBooking:
    """Test Booking aggregate"""
    
    def test_create_booking(self):
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
        assert booking.id == "test-1"
        assert booking.room_id == 1
        assert booking.guest_name == "John Doe"
        assert booking.status == BookingStatus.PENDING
        assert booking.get_nights_count() == 5
    
    def test_booking_invalid_dates_raises_error(self):
        with pytest.raises(ValueError, match="Check-in must be before check-out"):
            Booking(
                id="test-1",
                room_id=1,
                guest_name="John Doe",
                guest_email="john@example.com",
                check_in=date(2026, 6, 20),
                check_out=date(2026, 6, 15),
                status=BookingStatus.PENDING,
                total_price=Money(500.0, "USD"),
                created_at=datetime.now()
            )
    
    def test_booking_invalid_price_raises_error(self):
        with pytest.raises(ValueError, match="Total price must be positive"):
            Booking(
                id="test-1",
                room_id=1,
                guest_name="John Doe",
                guest_email="john@example.com",
                check_in=date(2026, 6, 15),
                check_out=date(2026, 6, 20),
                status=BookingStatus.PENDING,
                total_price=Money(0.0, "USD"),
                created_at=datetime.now()
            )
    
    def test_booking_invalid_email_raises_error(self):
        with pytest.raises(ValueError, match="Invalid email"):
            Booking(
                id="test-1",
                room_id=1,
                guest_name="John Doe",
                guest_email="invalid-email",
                check_in=date(2026, 6, 15),
                check_out=date(2026, 6, 20),
                status=BookingStatus.PENDING,
                total_price=Money(500.0, "USD"),
                created_at=datetime.now()
            )
    
    def test_cancel_booking(self):
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
        booking.cancel()
        assert booking.status == BookingStatus.CANCELLED
    
    def test_cancel_already_cancelled_booking_raises_error(self):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.CANCELLED,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        with pytest.raises(ValueError, match="Booking already cancelled"):
            booking.cancel()
    
    def test_confirm_booking(self):
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
        booking.confirm()
        assert booking.status == BookingStatus.CONFIRMED
    
    def test_confirm_non_pending_booking_raises_error(self):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.CONFIRMED,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        with pytest.raises(ValueError, match="Only pending bookings can be confirmed"):
            booking.confirm()
    
    def test_complete_booking(self):
        booking = Booking(
            id="test-1",
            room_id=1,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            status=BookingStatus.CONFIRMED,
            total_price=Money(500.0, "USD"),
            created_at=datetime.now()
        )
        booking.complete()
        assert booking.status == BookingStatus.COMPLETED
    
    def test_get_nights_count(self):
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
        assert booking.get_nights_count() == 5


class TestRoom:
    """Test Room entity"""
    
    def test_create_room(self):
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2
        )
        assert room.id == 1
        assert room.number == "101"
        assert room.is_available is True
    
    def test_room_invalid_capacity_raises_error(self):
        with pytest.raises(ValueError, match="Capacity must be positive"):
            Room(
                id=1,
                hotel_id=1,
                number="101",
                room_type="Standard",
                price_per_night=Money(100.0, "USD"),
                capacity=0
            )
    
    def test_room_book(self):
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2
        )
        room.book()
        assert room.is_available is False
    
    def test_room_book_already_booked_raises_error(self):
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2,
            is_available=False
        )
        with pytest.raises(ValueError, match="Room is not available"):
            room.book()
    
    def test_room_release(self):
        room = Room(
            id=1,
            hotel_id=1,
            number="101",
            room_type="Standard",
            price_per_night=Money(100.0, "USD"),
            capacity=2,
            is_available=False
        )
        room.release()
        assert room.is_available is True


class TestHotel:
    """Test Hotel aggregate"""
    
    def test_create_hotel(self):
        address = Address(
            street="123 Main St",
            city="New York",
            country="USA",
            postal_code="10001"
        )
        hotel = Hotel(
            id=1,
            name="Grand Hotel",
            address=address,
            rating=4.5,
            rooms=[]
        )
        assert hotel.name == "Grand Hotel"
        assert hotel.rating == 4.5
    
    def test_hotel_invalid_rating_raises_error(self):
        address = Address(
            street="123 Main St",
            city="New York",
            country="USA",
            postal_code="10001"
        )
        with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
            Hotel(
                id=1,
                name="Grand Hotel",
                address=address,
                rating=6.0,
                rooms=[]
            )
    
    def test_get_available_rooms(self):
        address = Address(
            street="123 Main St",
            city="New York",
            country="USA",
            postal_code="10001"
        )
        room1 = Room(1, 1, "101", "Standard", Money(100, "USD"), 2, True)
        room2 = Room(2, 1, "102", "Deluxe", Money(200, "USD"), 2, False)
        hotel = Hotel(
            id=1,
            name="Grand Hotel",
            address=address,
            rating=4.5,
            rooms=[room1, room2]
        )
        available = hotel.get_available_rooms()
        assert len(available) == 1
        assert available[0].number == "101"