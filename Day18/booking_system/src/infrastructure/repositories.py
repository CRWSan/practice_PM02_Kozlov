"""
Repository implementations
"""
from typing import Optional, List, Dict
from datetime import date
from ..core.domain import Booking, BookingStatus, Money, Room
from ..application.interfaces import IBookingRepository, IRoomRepository


class InMemoryBookingRepository(IBookingRepository):
    """In-memory implementation of booking repository"""
    
    def __init__(self):
        self._bookings: Dict[str, Booking] = {}
        self._id_counter = 1
    
    def save(self, booking: Booking) -> Booking:
        """Save a booking"""
        self._bookings[booking.id] = booking
        return booking
    
    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        return self._bookings.get(booking_id)
    
    def get_by_room_and_dates(self, room_id: int, check_in: date, check_out: date) -> List[Booking]:
        """Get bookings for a room in date range"""
        result = []
        for booking in self._bookings.values():
            if booking.room_id == room_id:
                # Check if booking overlaps with given dates
                if booking.check_in < check_out and booking.check_out > check_in:
                    result.append(booking)
        return result
    
    def get_by_guest_email(self, email: str) -> List[Booking]:
        """Get bookings by guest email"""
        result = []
        for booking in self._bookings.values():
            if booking.guest_email.lower() == email.lower():
                result.append(booking)
        return result
    
    def get_by_status(self, status: BookingStatus) -> List[Booking]:
        """Get bookings by status"""
        result = []
        for booking in self._bookings.values():
            if booking.status == status:
                result.append(booking)
        return result
    
    def delete(self, booking_id: str) -> None:
        """Delete a booking"""
        if booking_id in self._bookings:
            del self._bookings[booking_id]
    
    def clear(self) -> None:
        """Clear all bookings"""
        self._bookings.clear()


class InMemoryRoomRepository(IRoomRepository):
    """In-memory implementation of room repository"""
    
    def __init__(self):
        self._rooms: Dict[int, Room] = {}
        self._id_counter = 1
    
    def save(self, room: Room) -> Room:
        """Save a room"""
        if room.id is None:
            room.id = self._id_counter
            self._id_counter += 1
        self._rooms[room.id] = room
        return room
    
    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Get room by ID"""
        return self._rooms.get(room_id)
    
    def get_by_hotel(self, hotel_id: int) -> List[Room]:
        """Get all rooms for a hotel"""
        result = []
        for room in self._rooms.values():
            if room.hotel_id == hotel_id:
                result.append(room)
        return result
    
    def clear(self) -> None:
        """Clear all rooms"""
        self._rooms.clear()