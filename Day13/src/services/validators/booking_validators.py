from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import date

from src.domain.models import Room, Hotel, Booking
from src.domain.exceptions import (
    HotelRatingTooLowError,
    RoomNotFoundError,
    RoomNotAvailableError,
    BookingConflictError,
    InvalidDatesError
)
from src.repositories.booking_repo import BookingRepository
from src.repositories.hotel_repo import HotelRepository


class BookingValidator(ABC):
    """Абстрактный базовый класс для валидаторов (Chain of Responsibility)"""
    
    def __init__(self):
        self._next_validator: Optional['BookingValidator'] = None
    
    def set_next(self, validator: 'BookingValidator') -> 'BookingValidator':
        """Установить следующий валидатор в цепочке"""
        self._next_validator = validator
        return validator
    
    def validate(self, **kwargs) -> None:
        """Выполнить валидацию и передать дальше по цепочке"""
        self._validate(**kwargs)
        if self._next_validator:
            self._next_validator.validate(**kwargs)
    
    @abstractmethod
    def _validate(self, **kwargs) -> None:
        """Конкретная проверка для валидатора"""
        pass


class RoomExistsValidator(BookingValidator):
    """Проверка существования и активности номера"""
    
    def _validate(self, **kwargs) -> None:
        room: Room = kwargs.get('room')
        if not room:
            room_id = kwargs.get('room_id')
            room_repo = kwargs.get('room_repo')
            room = room_repo.get_by_id(room_id) if room_repo else None
        
        if not room:
            raise RoomNotFoundError(f"Номер {kwargs.get('room_id')} не найден")
        if not room.is_active:
            raise RoomNotFoundError(f"Номер {kwargs.get('room_id')} не активен")
        
        kwargs['room'] = room


class HotelRatingValidator(BookingValidator):
    """Проверка рейтинга отеля (Вариант 8)"""
    
    MIN_RATING = 3.0
    
    def _validate(self, **kwargs) -> None:
        room: Room = kwargs.get('room')
        hotel_repo: HotelRepository = kwargs.get('hotel_repo')
        
        if not room or not hotel_repo:
            raise BookingValidationError("Недостаточно данных для проверки рейтинга отеля")
        
        hotel = hotel_repo.get_by_id(room.hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель с ID {room.hotel_id} не найден")
        
        if hotel.rating < self.MIN_RATING:
            raise HotelRatingTooLowError(
                f"Бронирование недоступно: рейтинг отеля {hotel.rating} ниже минимального {self.MIN_RATING}",
                details={
                    "hotel_id": hotel.id,
                    "hotel_name": hotel.name,
                    "current_rating": hotel.rating,
                    "min_rating": self.MIN_RATING
                }
            )
        
        kwargs['hotel'] = hotel


class DateValidator(BookingValidator):
    """Проверка корректности дат"""
    
    MAX_DAYS = 30
    
    def _validate(self, **kwargs) -> None:
        check_in: date = kwargs.get('check_in')
        check_out: date = kwargs.get('check_out')
        
        if not check_in or not check_out:
            raise InvalidDatesError("Даты заезда и выезда обязательны")
        
        if check_out <= check_in:
            raise InvalidDatesError("Дата выезда должна быть позже даты заезда")
        
        if (check_out - check_in).days > self.MAX_DAYS:
            raise InvalidDatesError(f"Бронирование не может превышать {self.MAX_DAYS} дней")


class AvailabilityValidator(BookingValidator):
    """Проверка доступности номера на указанные даты"""
    
    def _validate(self, **kwargs) -> None:
        room_id: int = kwargs.get('room_id')
        check_in: date = kwargs.get('check_in')
        check_out: date = kwargs.get('check_out')
        booking_repo: BookingRepository = kwargs.get('booking_repo')
        
        if not all([room_id, check_in, check_out, booking_repo]):
            raise BookingValidationError("Недостаточно данных для проверки доступности")
        
        existing = booking_repo.get_by_room_and_dates(room_id, check_in, check_out)
        
        if existing:
            raise BookingConflictError(
                f"Номер {room_id} уже забронирован на эти даты",
                details={"conflicting_bookings": [b.id for b in existing]}
            )


class ValidatorChainBuilder:
    """Строитель цепочки валидаторов"""
    
    @staticmethod
    def build_for_booking() -> BookingValidator:
        """Создать цепочку валидаторов для бронирования"""
        # Строим цепочку: RoomExists -> HotelRating -> Date -> Availability
        room_validator = RoomExistsValidator()
        hotel_validator = HotelRatingValidator()
        date_validator = DateValidator()
        availability_validator = AvailabilityValidator()
        
        room_validator.set_next(hotel_validator)
        hotel_validator.set_next(date_validator)
        date_validator.set_next(availability_validator)
        
        return room_validator