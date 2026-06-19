from pydantic import BaseModel, validator, field_validator
from datetime import date, datetime
from typing import Optional


class BookingCreateDTO(BaseModel):
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    
    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v, info) -> date:
        if 'check_in' in info.data and v <= info.data['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if (v - info.data['check_in']).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v


class BookingResponseDTO(BaseModel):
    id: int
    room_id: int
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime


class BookingUpdateDTO(BaseModel):
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None


class BookingErrorResponseDTO(BaseModel):
    error: str
    details: Optional[dict] = None