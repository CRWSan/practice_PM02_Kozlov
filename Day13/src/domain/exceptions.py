class DomainError(Exception):
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class RoomNotFoundError(DomainError):
    pass

class RoomNotAvailableError(DomainError):
    pass

class BookingNotFoundError(DomainError):
    pass

class BookingConflictError(DomainError):
    pass

class InvalidDatesError(DomainError):
    pass

class HotelNotFoundError(DomainError):
    pass

class HotelRatingTooLowError(DomainError):
    pass

class BookingValidationError(DomainError):
    pass