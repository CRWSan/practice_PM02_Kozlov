"""
Validators
"""
import re
from datetime import date
from typing import Optional


class Validators:
    """Collection of validation functions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return len(cleaned) >= 10 and cleaned.isdigit()
    
    @staticmethod
    def validate_date_range(check_in: date, check_out: date) -> bool:
        """Validate date range"""
        if not check_in or not check_out:
            return False
        return check_in < check_out
    
    @staticmethod
    def validate_room_number(room_number: str) -> bool:
        """Validate room number"""
        if not room_number:
            return False
        return bool(re.match(r'^[A-Z0-9\-]+$', room_number))
    
    @staticmethod
    def validate_guest_name(name: str) -> bool:
        """Validate guest name"""
        if not name:
            return False
        return len(name.strip()) >= 2 and len(name.strip()) <= 100
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input string"""
        if not text:
            return ""
        # Remove potential dangerous characters
        return re.sub(r'[<>"\'()]', '', text).strip()