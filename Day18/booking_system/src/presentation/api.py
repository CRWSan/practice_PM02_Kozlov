"""
REST API
"""
from typing import Optional, List
from datetime import datetime, date
from ..application.services import BookingService, HotelService
from ..application.dto import BookingCreateDTO
from ..core.exceptions import BookingNotFoundError, RoomNotFoundError


class BookingAPI:
    """REST API for booking operations"""
    
    def __init__(self, booking_service: BookingService, hotel_service: HotelService):
        self.booking_service = booking_service
        self.hotel_service = hotel_service
    
    def create_booking(self, data: dict) -> dict:
        """
        POST /api/bookings
        """
        try:
            dto = BookingCreateDTO(
                room_id=data['room_id'],
                guest_name=data['guest_name'],
                guest_email=data['guest_email'],
                check_in=datetime.strptime(data['check_in'], '%Y-%m-%d').date(),
                check_out=datetime.strptime(data['check_out'], '%Y-%m-%d').date(),
                guest_phone=data.get('guest_phone')
            )
            booking = self.booking_service.create_booking(dto)
            return {
                'status': 'success',
                'data': self.booking_service.get_booking_response_dto(booking)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def cancel_booking(self, booking_id: str) -> dict:
        """
        POST /api/bookings/{id}/cancel
        """
        try:
            booking = self.booking_service.cancel_booking(booking_id)
            return {
                'status': 'success',
                'data': self.booking_service.get_booking_response_dto(booking)
            }
        except BookingNotFoundError as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_booking(self, booking_id: str) -> dict:
        """
        GET /api/bookings/{id}
        """
        booking = self.booking_service.get_booking(booking_id)
        if booking:
            return {
                'status': 'success',
                'data': self.booking_service.get_booking_response_dto(booking)
            }
        return {
            'status': 'error',
            'message': f'Booking {booking_id} not found'
        }
    
    def search_rooms(self, params: dict) -> dict:
        """
        GET /api/rooms/search
        """
        try:
            rooms = self.hotel_service.search_rooms(
                hotel_id=params['hotel_id'],
                check_in=datetime.strptime(params['check_in'], '%Y-%m-%d').date(),
                check_out=datetime.strptime(params['check_out'], '%Y-%m-%d').date(),
                capacity=params.get('capacity')
            )
            return {
                'status': 'success',
                'data': [
                    {
                        'id': room.id,
                        'number': room.number,
                        'type': room.room_type,
                        'price_per_night': room.price_per_night.amount,
                        'currency': room.price_per_night.currency,
                        'capacity': room.capacity
                    }
                    for room in rooms
                ]
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }