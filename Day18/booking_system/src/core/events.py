"""
Domain Events
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Callable
from .domain import Booking


@dataclass
class DomainEvent:
    """Base domain event"""
    event_id: str
    occurred_on: datetime
    event_type: str


@dataclass
class BookingCreatedEvent(DomainEvent):
    """Event when booking is created"""
    booking: Booking


@dataclass
class BookingCancelledEvent(DomainEvent):
    """Event when booking is cancelled"""
    booking: Booking
    reason: str = ""


@dataclass
class BookingConfirmedEvent(DomainEvent):
    """Event when booking is confirmed"""
    booking: Booking


@dataclass
class PaymentCompletedEvent(DomainEvent):
    """Event when payment is completed"""
    booking_id: str
    amount: float


class EventDispatcher:
    """Simple event dispatcher"""
    def __init__(self):
        self._handlers: dict = {}
    
    def register(self, event_type: str, handler: Callable) -> None:
        """Register a handler for event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch event to all registered handlers"""
        event_type = event.event_type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
    
    def clear(self) -> None:
        """Clear all handlers"""
        self._handlers.clear()