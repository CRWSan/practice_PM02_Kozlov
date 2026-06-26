"""
CQRS: Commands and Queries
"""
from datetime import date
from typing import Optional, List
import uuid

from ..core.domain import Booking, BookingStatus, Money, Room
from ..core.exceptions import (
    BookingNotFoundError, RoomNotFoundError, 
    RoomNotAvailableError, InvalidBookingDataError
)
from .dto import BookingCreateDTO, BookingResponseDTO
from .interfaces import IBookingRepository, IRoomRepository, IPaymentService


class BookingService:
    """Booking service with CQRS pattern"""
    
    def __init__(self, booking_repo: IBookingRepository, 
                 room_repo: IRoomRepository,
                 payment_service: Optional[IPaymentService] = None):
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.payment_service = payment_service
    
    def create_booking(self, dto: BookingCreateDTO) -> Booking:
        """
        Create a new booking
        """
        # Validate dates
        if dto.check_in >= dto.check_out:
            raise InvalidBookingDataError("Check-in must be before check-out")
        
        # Get room
        room = self.room_repo.get_by_id(dto.room_id)
        if not room:
            raise RoomNotFoundError(dto.room_id)
        
        # Check availability
        if not self.is_room_available(dto.room_id, dto.check_in, dto.check_out):
            raise RoomNotAvailableError(dto.room_id, dto.check_in, dto.check_out)
        
        # Calculate total price
        nights = (dto.check_out - dto.check_in).days
        total_amount = room.price_per_night.amount * nights
        
        # Create booking
        booking = Booking(
            id=str(uuid.uuid4()),
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            status=BookingStatus.PENDING,
            total_price=Money(total_amount, room.price_per_night.currency),
            created_at=date.today(),
            guest_phone=dto.guest_phone
        )
        
        # Save
        self.booking_repo.save(booking)
        
        return booking
    
    def cancel_booking(self, booking_id: str) -> Booking:
        """Cancel a booking"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(booking_id)
        
        # CANCEL THE BOOKING (FIXED: Change status instead of deleting)
        booking.cancel()
        self.booking_repo.save(booking)
        
        return booking
    
    def confirm_booking(self, booking_id: str) -> Booking:
        """Confirm a booking"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(booking_id)
        
        booking.confirm()
        self.booking_repo.save(booking)
        
        # Process payment if payment service is available
        if self.payment_service:
            self.payment_service.process_payment(booking_id, booking.total_price.amount)
        
        return booking
    
    def complete_booking(self, booking_id: str) -> Booking:
        """Complete a booking"""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(booking_id)
        
        booking.complete()
        self.booking_repo.save(booking)
        
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        return self.booking_repo.get_by_id(booking_id)
    
    def get_bookings_by_email(self, email: str) -> List[Booking]:
        """Get bookings by guest email"""
        return self.booking_repo.get_by_guest_email(email)
    
    def is_room_available(self, room_id: int, check_in: date, check_out: date) -> bool:
        """
        Check if room is available for given dates
        FIXED: Proper overlap check and ignore CANCELLED bookings
        """
        bookings = self.booking_repo.get_by_room_and_dates(room_id, check_in, check_out)
        
        for booking in bookings:
            # FIXED: Skip CANCELLED bookings
            if booking.status == BookingStatus.CANCELLED:
                continue
            
            # FIXED: Proper date overlap condition
            # A booking overlaps if: start < existing_end AND end > existing_start
            if booking.check_in < check_out and booking.check_out > check_in:
                return False
        
        return True
    
    def get_booking_response_dto(self, booking: Booking) -> BookingResponseDTO:
        """Convert booking to response DTO"""
        return BookingResponseDTO(
            id=booking.id,
            room_id=booking.room_id,
            guest_name=booking.guest_name,
            guest_email=booking.guest_email,
            check_in=booking.check_in,
            check_out=booking.check_out,
            status=booking.status.value,
            total_price=booking.total_price.amount,
            currency=booking.total_price.currency,
            nights=booking.get_nights_count(),
            created_at=booking.created_at.isoformat() if booking.created_at else ""
        )


class HotelService:
    """Hotel service"""
    
    def __init__(self, room_repo: IRoomRepository):
        self.room_repo = room_repo
    
    def search_rooms(self, hotel_id: int, check_in: date, 
                     check_out: date, capacity: Optional[int] = None) -> List[Room]:
        """Search available rooms"""
        rooms = self.room_repo.get_by_hotel(hotel_id)
        
        # Filter by availability (simplified)
        available_rooms = [room for room in rooms if room.is_available]
        
        # Filter by capacity
        if capacity:
            available_rooms = [room for room in available_rooms 
                             if room.capacity >= capacity]
        
        return available_rooms