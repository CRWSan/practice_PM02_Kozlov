"""
Unit tests for validators
"""
import pytest
from datetime import date
from src.utils.validators import Validators


class TestValidators:
    """Test validator functions"""
    
    def test_validate_email_valid(self):
        assert Validators.validate_email("john@example.com") is True
        assert Validators.validate_email("jane.doe@test.org") is True
        assert Validators.validate_email("user+tag@gmail.com") is True
    
    def test_validate_email_invalid(self):
        assert Validators.validate_email("invalid-email") is False
        assert Validators.validate_email("john@") is False
        assert Validators.validate_email("@example.com") is False
        assert Validators.validate_email("john@example..com") is False
    
    def test_validate_email_empty(self):
        assert Validators.validate_email("") is False
        assert Validators.validate_email(None) is False
    
    def test_validate_phone_valid(self):
        assert Validators.validate_phone("+1234567890") is True
        assert Validators.validate_phone("1234567890") is True
        assert Validators.validate_phone("+1 (234) 567-890") is True
    
    def test_validate_phone_invalid(self):
        assert Validators.validate_phone("123") is False
        assert Validators.validate_phone("abcdefghij") is False
        assert Validators.validate_phone("") is False
    
    def test_validate_date_range_valid(self):
        assert Validators.validate_date_range(
            date(2026, 6, 15), 
            date(2026, 6, 20)
        ) is True
    
    def test_validate_date_range_invalid(self):
        assert Validators.validate_date_range(
            date(2026, 6, 20),
            date(2026, 6, 15)
        ) is False
        assert Validators.validate_date_range(None, date(2026, 6, 15)) is False
    
    def test_validate_room_number_valid(self):
        assert Validators.validate_room_number("101") is True
        assert Validators.validate_room_number("A-101") is True
        assert Validators.validate_room_number("10A") is True
    
    def test_validate_room_number_invalid(self):
        assert Validators.validate_room_number("") is False
        assert Validators.validate_room_number("!@#") is False
    
    def test_validate_guest_name_valid(self):
        assert Validators.validate_guest_name("John Doe") is True
        assert Validators.validate_guest_name("A") is False  # Too short
        assert Validators.validate_guest_name("a" * 101) is False  # Too long
    
    def test_sanitize_input(self):
        assert Validators.sanitize_input("Hello") == "Hello"
        assert Validators.sanitize_input("Hello <script>") == "Hello script"
        assert Validators.sanitize_input("") == ""
        assert Validators.sanitize_input('"quote"') == "quote"