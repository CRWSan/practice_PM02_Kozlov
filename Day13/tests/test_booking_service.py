import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from src.services.booking_service import BookingService
from src.services.pricing_service import PricingService
from src.uow.unit_of_work import UnitOfWork
from src.dto.booking_dto import BookingCreateDTO
from src.domain.models import Hotel, Room, Booking, BookingStatus
from src.domain.exceptions import (
    RoomNotFoundError, BookingConflictError,
    HotelRatingTooLowError, HotelNotFoundError
)


class TestBookingService:
    
    def test_create_booking_success(self, booking_service, uow):
        """Успешное создание бронирования для отеля с высоким рейтингом"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Premium Hotel", address="123 St",
            phone="+123", rating=4.5
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=hotel.id, number="101",
            capacity=2, price_per_night=100.0
        ))
        
        dto = BookingCreateDTO(
            room_id=room.id,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20)
        )
        
        # Act
        result = booking_service.create(dto)
        
        # Assert
        assert result.id is not None
        assert result.room_id == room.id
        assert result.total_price > 0
        
    def test_create_booking_hotel_rating_too_low(self, booking_service, uow):
        """Ошибка при бронировании в отеле с низким рейтингом (< 3.0)"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Low Rating Hotel", address="456 St",
            phone="+456", rating=2.5  # Ниже 3.0
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=hotel.id, number="102",
            capacity=2, price_per_night=100.0
        ))
        
        dto = BookingCreateDTO(
            room_id=room.id,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20)
        )
        
        # Act & Assert
        with pytest.raises(HotelRatingTooLowError) as exc_info:
            booking_service.create(dto)
        
        assert "рейтинг отеля" in str(exc_info.value).lower()
        assert "2.5" in str(exc_info.value)
    
    def test_create_booking_hotel_rating_exactly_minimum(self, booking_service, uow):
        """Успешное бронирование в отеле с рейтингом точно 3.0"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Minimum Rating Hotel", address="789 St",
            phone="+789", rating=3.0  # Точно минимальный
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=hotel.id, number="103",
            capacity=2, price_per_night=100.0
        ))
        
        dto = BookingCreateDTO(
            room_id=room.id,
            guest_name="Bob Smith",
            guest_email="bob@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20)
        )
        
        # Act
        result = booking_service.create(dto)
        
        # Assert
        assert result.id is not None
        assert result.room_id == room.id
    
    def test_get_available_rooms_with_rating_filter(self, booking_service, uow):
        """Получение доступных номеров с фильтром по рейтингу"""
        # Arrange
        hotel1 = uow.hotels.add(Hotel(
            id=None, name="Good Hotel", address="111 St",
            phone="+111", rating=4.2
        ))
        hotel2 = uow.hotels.add(Hotel(
            id=None, name="Bad Hotel", address="222 St",
            phone="+222", rating=2.8
        ))
        
        room1 = uow.rooms.add(Room(
            id=None, hotel_id=hotel1.id, number="201",
            capacity=2, price_per_night=100.0
        ))
        room2 = uow.rooms.add(Room(
            id=None, hotel_id=hotel2.id, number="202",
            capacity=2, price_per_night=80.0
        ))
        
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        # Act - поиск с минимальным рейтингом 3.0
        available = booking_service.get_available_rooms(
            hotel_id=hotel1.id,
            check_in=check_in,
            check_out=check_out,
            min_rating=3.0
        )
        
        # Assert
        assert len(available) == 1
        assert available[0]['room_id'] == room1.id
        assert available[0]['hotel_rating'] == 4.2
    
    def test_get_available_rooms_hotel_rating_too_low(self, booking_service, uow):
        """Ошибка при попытке получить номера из отеля с низким рейтингом"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Low Rating Hotel", address="333 St",
            phone="+333", rating=2.5
        ))
        
        check_in = date(2026, 6, 15)
        check_out = date(2026, 6, 20)
        
        # Act & Assert
        with pytest.raises(HotelRatingTooLowError) as exc_info:
            booking_service.get_available_rooms(
                hotel_id=hotel.id,
                check_in=check_in,
                check_out=check_out,
                min_rating=3.0
            )
        
        assert "рейтинг" in str(exc_info.value).lower()
    
    def test_booking_conflict_prevents_creation(self, booking_service, uow):
        """Ошибка при попытке бронирования занятого номера"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Test Hotel", address="444 St",
            phone="+444", rating=4.0
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=hotel.id, number="301",
            capacity=2, price_per_night=100.0
        ))
        
        # Создаем существующее бронирование
        existing = Booking(
            id=None,
            room_id=room.id,
            guest_name="Existing Guest",
            guest_email="existing@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 18),
            total_price=300.0,
            status=BookingStatus.CONFIRMED
        )
        uow.bookings.add(existing)
        uow.commit()
        
        # Пытаемся забронировать с пересечением
        dto = BookingCreateDTO(
            room_id=room.id,
            guest_name="New Guest",
            guest_email="new@example.com",
            check_in=date(2026, 6, 16),
            check_out=date(2026, 6, 19)
        )
        
        # Act & Assert
        with pytest.raises(BookingConflictError):
            booking_service.create(dto)
    
    def test_cancel_booking_success(self, booking_service, uow):
        """Успешная отмена бронирования"""
        # Arrange
        hotel = uow.hotels.add(Hotel(
            id=None, name="Test Hotel", address="555 St",
            phone="+555", rating=4.0
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=hotel.id, number="401",
            capacity=2, price_per_night=100.0
        ))
        
        booking = Booking(
            id=None,
            room_id=room.id,
            guest_name="Cancel Guest",
            guest_email="cancel@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20),
            total_price=500.0,
            status=BookingStatus.PENDING
        )
        saved = uow.bookings.add(booking)
        uow.commit()
        
        # Act
        result = booking_service.cancel(saved.id)
        
        # Assert
        assert result is True
        cancelled = uow.bookings.get_by_id(saved.id)
        assert cancelled.status == BookingStatus.CANCELLED
        assert cancelled.cancelled_at is not None
    
    def test_chain_of_responsibility_order(self, booking_service, uow):
        """Проверка порядка выполнения валидаторов в цепочке"""
        # Создаем отель с высоким рейтингом, но номер не существует
        hotel = uow.hotels.add(Hotel(
            id=None, name="Test Hotel", address="666 St",
            phone="+666", rating=4.5
        ))
        
        dto = BookingCreateDTO(
            room_id=999,  # Несуществующий номер
            guest_name="Test Guest",
            guest_email="test@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20)
        )
        
        # Должна быть ошибка RoomNotFoundError (первый валидатор)
        with pytest.raises(RoomNotFoundError):
            booking_service.create(dto)
        
        # Теперь создаем номер для отеля с низким рейтингом
        low_rating_hotel = uow.hotels.add(Hotel(
            id=None, name="Low Rating Hotel", address="777 St",
            phone="+777", rating=2.0
        ))
        room = uow.rooms.add(Room(
            id=None, hotel_id=low_rating_hotel.id, number="501",
            capacity=2, price_per_night=100.0
        ))
        
        dto2 = BookingCreateDTO(
            room_id=room.id,
            guest_name="Test Guest 2",
            guest_email="test2@example.com",
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 20)
        )
        
        # Должна быть ошибка HotelRatingTooLowError (второй валидатор)
        with pytest.raises(HotelRatingTooLowError):
            booking_service.create(dto2)