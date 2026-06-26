"""
Integration tests for API
"""
import pytest
from datetime import date, datetime
from src.application.services import BookingService, HotelService
from src.infrastructure.repositories import InMemoryBookingRepository, InMemoryRoomRepository
from src.presentation.api import BookingAPI
from src.core.domain import Room, Money


class TestBookingAPI:
    """Test BookingAPI"""
    
    @pytest.fixture
    def api(self):
        booking_repo = InMemoryBookingRepository()
        room_repo = InMemoryRoomRepository()
        
        # Add test room
        room = Room(1, 1, "101", "Standard", Money(100, "USD"), 2)
        room_repo.save(room)
        
        booking_service = BookingService(booking_repo, room_repo)
        hotel_service = HotelService(room_repo)
        
        return BookingAPI(booking_service, hotel_service)
    
    def test_create_booking_success(self, api):
        data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "check_in": "2026-06-15",
            "check_out": "2026-06-20",
            "guest_phone": "+1234567890"
        }
        
        result = api.create_booking(data)
        assert result["status"] == "success"
        assert result["data"]["guest_name"] == "John Doe"
        assert result["data"]["total_price"] == 500.0
    
    def test_create_booking_invalid_dates(self, api):
        data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "check_in": "2026-06-20",
            "check_out": "2026-06-15",
            "guest_phone": "+1234567890"
        }
        
        result = api.create_booking(data)
        assert result["status"] == "error"
    
    def test_create_booking_room_not_found(self, api):
        data = {
            "room_id": 999,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "check_in": "2026-06-15",
            "check_out": "2026-06-20",
            "guest_phone": "+1234567890"
        }
        
        result = api.create_booking(data)
        assert result["status"] == "error"
    
    def test_cancel_booking_success(self, api):
        # Create booking first
        data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "check_in": "2026-06-15",
            "check_out": "2026-06-20",
            "guest_phone": "+1234567890"
        }
        result = api.create_booking(data)
        booking_id = result["data"]["id"]
        
        # Cancel
        cancel_result = api.cancel_booking(booking_id)
        assert cancel_result["status"] == "success"
        assert cancel_result["data"]["status"] == "cancelled"
    
    def test_cancel_booking_not_found(self, api):
        result = api.cancel_booking("non-existent")
        assert result["status"] == "error"
    
    def test_get_booking_success(self, api):
        # Create booking first
        data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "check_in": "2026-06-15",
            "check_out": "2026-06-20",
            "guest_phone": "+1234567890"
        }
        result = api.create_booking(data)
        booking_id = result["data"]["id"]
        
        # Get booking
        get_result = api.get_booking(booking_id)
        assert get_result["status"] == "success"
        assert get_result["data"]["id"] == booking_id
    
    def test_search_rooms_success(self, api):
        params = {
            "hotel_id": 1,
            "check_in": "2026-06-15",
            "check_out": "2026-06-20"
        }
        
        result = api.search_rooms(params)
        assert result["status"] == "success"
        assert len(result["data"]) >= 1