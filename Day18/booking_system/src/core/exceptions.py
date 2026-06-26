"""
Custom exceptions
"""


class BookingError(Exception):
    """Base exception for booking errors"""
    pass


class BookingNotFoundError(BookingError):
    """Raised when booking is not found"""
    def __init__(self, booking_id: str):
        self.booking_id = booking_id
        super().__init__(f"Booking with ID {booking_id} not found")


class RoomNotFoundError(BookingError):
    """Raised when room is not found"""
    def __init__(self, room_id: int):
        self.room_id = room_id
        super().__init__(f"Room with ID {room_id} not found")


class RoomNotAvailableError(BookingError):
    """Raised when room is not available"""
    def __init__(self, room_id: int, check_in, check_out):
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        super().__init__(f"Room {room_id} not available for dates {check_in} - {check_out}")


class InvalidBookingDataError(BookingError):
    """Raised when booking data is invalid"""
    pass


class PaymentError(Exception):
    """Base exception for payment errors"""
    pass


class PaymentFailedError(PaymentError):
    """Raised when payment fails"""
    pass


class HotelNotFoundError(BookingError):
    """Raised when hotel is not found"""
    def __init__(self, hotel_id: int):
        self.hotel_id = hotel_id
        super().__init__(f"Hotel with ID {hotel_id} not found")


class DiscountError(Exception):
    """Base exception for discount errors"""
    pass