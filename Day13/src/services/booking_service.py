from datetime import date, datetime, timedelta
from typing import List, Optional

from src.domain.models import Booking, BookingStatus
from src.domain.exceptions import (
    RoomNotFoundError, RoomNotAvailableError,
    BookingConflictError, BookingNotFoundError, 
    InvalidDatesError, HotelRatingTooLowError
)
from src.dto.booking_dto import BookingCreateDTO, BookingResponseDTO, BookingUpdateDTO
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.validators.booking_validators import ValidatorChainBuilder


class BookingService:
    """Сервис для управления бронированиями с валидацией рейтинга отеля"""
    
    def __init__(self, uow: UnitOfWork, pricing_service: PricingService):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms
        self.hotel_repo = uow.hotels
        
        # Создаем цепочку валидаторов
        self.validator_chain = ValidatorChainBuilder.build_for_booking()
    
    def _validate_booking_data(self, dto: BookingCreateDTO) -> None:
        """
        Валидация данных бронирования с использованием Chain of Responsibility.
        Включает проверку рейтинга отеля (Вариант 8).
        """
        # Получаем номер для проверки существования
        room = self.room_repo.get_by_id(dto.room_id)
        
        self.validator_chain.validate(
            room_id=dto.room_id,
            room=room,
            check_in=dto.check_in,
            check_out=dto.check_out,
            room_repo=self.room_repo,
            hotel_repo=self.hotel_repo,
            booking_repo=self.booking_repo
        )
    
    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        """Создать новое бронирование с проверкой рейтинга отеля"""
        
        # 1. Валидация через цепочку (включая проверку рейтинга отеля)
        self._validate_booking_data(dto)
        
        # 2. Получаем номер (уже проверен валидатором)
        room = self.room_repo.get_by_id(dto.room_id)
        
        # 3. Рассчитываем стоимость
        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )
        
        # 4. Создаем бронирование
        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING
        )
        
        # 5. Сохраняем
        saved = self.booking_repo.add(booking)
        self.uow.commit()
        
        return BookingResponseDTO(
            id=saved.id,
            room_id=saved.room_id,
            guest_name=saved.guest_name,
            check_in=saved.check_in,
            check_out=saved.check_out,
            total_price=saved.total_price,
            status=saved.status.value,
            created_at=saved.created_at
        )
    
    def cancel(self, booking_id: int) -> bool:
        """Отменить бронирование"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")
        
        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise DomainError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )
        
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        self.booking_repo.update(booking)
        self.uow.commit()
        return True
    
    def get_available_rooms(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        capacity: Optional[int] = None,
        min_rating: Optional[float] = None
    ) -> List[dict]:
        """
        Получить доступные номера в отеле на указанные даты.
        Вариант 8: дополнительная проверка рейтинга отеля.
        """
        # 1. Проверяем рейтинг отеля
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель с ID {hotel_id} не найден")
        
        if min_rating and hotel.rating < min_rating:
            raise HotelRatingTooLowError(
                f"Рейтинг отеля {hotel.rating} ниже минимального {min_rating}"
            )
        
        # 2. Получаем все номера отеля
        rooms = self.room_repo.get_by_hotel(hotel_id, active_only=True)
        
        # 3. Фильтруем по вместимости
        if capacity:
            rooms = [r for r in rooms if r.capacity >= capacity]
        
        # 4. Для каждого номера проверяем доступность
        available = []
        for room in rooms:
            existing = self.booking_repo.get_by_room_and_dates(
                room.id, check_in, check_out
            )
            if not existing:
                available.append({
                    'room_id': room.id,
                    'number': room.number,
                    'capacity': room.capacity,
                    'price_per_night': room.price_per_night,
                    'hotel_rating': hotel.rating
                })
        
        return available
    
    def confirm(self, booking_id: int) -> None:
        """Подтвердить бронирование (администратор)"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")
        
        if booking.status != BookingStatus.PENDING:
            raise DomainError(
                f"Бронирование в статусе {booking.status.value} нельзя подтвердить"
            )
        
        booking.status = BookingStatus.CONFIRMED
        self.booking_repo.update(booking)
        self.uow.commit()
    
    def get_by_id(self, booking_id: int) -> Optional[BookingResponseDTO]:
        """Получить бронирование по ID"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            return None
        
        return BookingResponseDTO(
            id=booking.id,
            room_id=booking.room_id,
            guest_name=booking.guest_name,
            check_in=booking.check_in,
            check_out=booking.check_out,
            total_price=booking.total_price,
            status=booking.status.value,
            created_at=booking.created_at
        )