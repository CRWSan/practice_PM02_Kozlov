"""
Unit of Work pattern
"""
from typing import Optional
from .repositories import InMemoryBookingRepository, InMemoryRoomRepository


class UnitOfWork:
    """Unit of Work for managing transactions"""
    
    def __init__(self):
        self.booking_repo = InMemoryBookingRepository()
        self.room_repo = InMemoryRoomRepository()
        self._is_active = False
    
    def __enter__(self):
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
    
    def begin(self) -> None:
        """Begin transaction"""
        self._is_active = True
    
    def commit(self) -> None:
        """Commit transaction"""
        self._is_active = False
    
    def rollback(self) -> None:
        """Rollback transaction"""
        self._is_active = False