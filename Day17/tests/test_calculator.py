# tests/test_calculator.py
import pytest
from src.calculator import (
    calculate_discount,
    calculate_total_with_tax,
    calculate_average_rating,
    is_room_available
)

# --- Тесты для calculate_discount ---

def test_calculate_discount_basic():
    result = calculate_discount(1000, 3, False)
    assert result == 100

def test_calculate_discount_vip():
    result = calculate_discount(1000, 3, True)
    assert result == 150

def test_calculate_discount_max():
    result = calculate_discount(1000, 15, True)
    assert result == 500

def test_calculate_discount_zero_price():
    result = calculate_discount(0, 3, False)
    assert result == 0

def test_calculate_discount_zero_nights():
    result = calculate_discount(1000, 0, False)
    assert result == 0

@pytest.mark.parametrize("price, nights, vip, expected", [
    (1000, 1, False, 0),
    (1000, 2, False, 0),
    (1000, 3, False, 100),
    (1000, 6, False, 200),
    (1000, 3, True, 150),
    (1000, 6, True, 250),
])
def test_calculate_discount_parametrized(price, nights, vip, expected):
    assert calculate_discount(price, nights, vip) == expected

# --- Тесты для calculate_total_with_tax ---

def test_calculate_total_with_tax_basic():
    result = calculate_total_with_tax(1000)
    assert result == 1180.0

def test_calculate_total_with_tax_custom_rate():
    result = calculate_total_with_tax(1000, 0.20)
    assert result == 1200.0

def test_calculate_total_with_tax_negative_price():
    result = calculate_total_with_tax(-100)
    assert result == 0.0

# --- Тесты для calculate_average_rating ---

def test_calculate_average_rating_basic():
    ratings = [4, 5, 3, 4]
    result = calculate_average_rating(ratings)
    assert result == 4.0

def test_calculate_average_rating_empty():
    result = calculate_average_rating([])
    assert result == 0.0

def test_calculate_average_rating_single():
    result = calculate_average_rating([5])
    assert result == 5.0

# === ТЕСТЫ ДЛЯ is_room_available ===

def test_is_room_available_free():
    """Номер свободен, если нет бронирований"""
    bookings = []
    result = is_room_available(bookings, '2026-06-15', '2026-06-20', 1)
    assert result == True

def test_is_room_available_booked():
    """Номер занят, если есть пересечение"""
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-10', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-15', '2026-06-20', 1)
    assert result == False

def test_is_room_available_different_room():
    """Занят другой номер - наш номер свободен"""
    bookings = [
        {'room_id': 2, 'check_in': '2026-06-10', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-15', '2026-06-20', 1)
    assert result == True

# === ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ is_room_available ===

def test_is_room_available_edge_case_same_day():
    """
    Проверка: check_in == check_out
    Бронирование: 15-16
    Запрос: 15-15
    Ожидание: ЗАНЯТ (потому что 15-е занято)
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-16'}
    ]
    result = is_room_available(bookings, '2026-06-15', '2026-06-15', 1)
    assert result == False  # ЗАНЯТ

def test_is_room_available_edge_case_check_out():
    """
    Проверка: запрос начинается в день выезда
    Бронирование: 15-18
    Запрос: 18-20
    Ожидание: СВОБОДЕН (день выезда не считается занятым)
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-18', '2026-06-20', 1)
    assert result == True  # СВОБОДЕН

def test_is_room_available_edge_case_check_in():
    """
    Проверка: запрос заканчивается в день заезда
    Бронирование: 15-18
    Запрос: 10-15
    Ожидание: СВОБОДЕН? НЕТ! 15-е занято, значит номер НЕ доступен
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-10', '2026-06-15', 1)
    assert result == False  # ЗАНЯТ (потому что 15-е занято)

def test_is_room_available_before_booking():
    """
    Проверка: запрос до бронирования
    Бронирование: 15-18
    Запрос: 10-14
    Ожидание: СВОБОДЕН
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-10', '2026-06-14', 1)
    assert result == True  # СВОБОДЕН

def test_is_room_available_after_booking():
    """
    Проверка: запрос после бронирования
    Бронирование: 15-18
    Запрос: 19-20
    Ожидание: СВОБОДЕН
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-19', '2026-06-20', 1)
    assert result == True  # СВОБОДЕН

def test_is_room_available_exact_booking_period():
    """
    Проверка: запрос точно совпадает с бронированием
    Бронирование: 15-18
    Запрос: 15-18
    Ожидание: ЗАНЯТ
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-15', '2026-06-18', 1)
    assert result == False  # ЗАНЯТ

def test_is_room_available_inside_booking():
    """
    Проверка: запрос внутри бронирования
    Бронирование: 15-18
    Запрос: 16-17
    Ожидание: ЗАНЯТ
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'}
    ]
    result = is_room_available(bookings, '2026-06-16', '2026-06-17', 1)
    assert result == False  # ЗАНЯТ

def test_is_room_available_multiple_bookings():
    """
    Проверка с несколькими бронированиями
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-10', 'check_out': '2026-06-12'},
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-18'},
        {'room_id': 2, 'check_in': '2026-06-10', 'check_out': '2026-06-20'}
    ]
    # Номер 1 свободен между 12 и 15
    result = is_room_available(bookings, '2026-06-13', '2026-06-14', 1)
    assert result == True  # СВОБОДЕН
    # Номер 1 занят 11-го
    result = is_room_available(bookings, '2026-06-11', '2026-06-13', 1)
    assert result == False  # ЗАНЯТ
    # Номер 2 занят весь период
    result = is_room_available(bookings, '2026-06-11', '2026-06-19', 2)
    assert result == False  # ЗАНЯТ

def test_room_available_mutation_less_than():
    """
    Тест для мутации: проверка условия < vs <=
    Бронирование: 15-16
    Запрос: 15-15 (check_in == check_out)
    Ожидание: ЗАНЯТ
    """
    bookings = [
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-16'}
    ]
    result = is_room_available(bookings, '2026-06-15', '2026-06-15', 1)
    assert result == False  # ЗАНЯТ

# === ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ ДРУГИХ ФУНКЦИЙ ===

def test_calculate_discount_negative_price_positive_nights():
    result = calculate_discount(-100, 3, False)
    assert result == 0

def test_calculate_discount_positive_price_zero_nights():
    result = calculate_discount(1000, 0, False)
    assert result == 0

def test_calculate_discount_positive_price_negative_nights():
    result = calculate_discount(1000, -3, False)
    assert result == 0

def test_calculate_discount_max_limit_exact():
    result = calculate_discount(1000, 30, False)
    assert result == 500

def test_calculate_discount_max_limit_beyond():
    result = calculate_discount(1000, 33, False)
    assert result == 500

def test_calculate_discount_vip_with_max():
    result = calculate_discount(1000, 15, True)
    assert result == 500

def test_calculate_average_rating_decimals():
    ratings = [4.5, 3.5, 4.0]
    result = calculate_average_rating(ratings)
    assert result == 4.0

def test_calculate_average_rating_large_numbers():
    ratings = [100, 200, 300]
    result = calculate_average_rating(ratings)
    assert result == 200.0

def test_calculate_average_rating_with_zero():
    ratings = [0, 5, 4]
    result = calculate_average_rating(ratings)
    assert result == 3.0

def test_calculate_total_with_tax_edge_cases():
    assert calculate_total_with_tax(0) == 0.0
    assert calculate_total_with_tax(0, 0.10) == 0.0
    assert calculate_total_with_tax(100, 0) == 100.0
    assert calculate_total_with_tax(100, 0.0) == 100.0

def test_calculate_total_with_tax_rounding():
    result = calculate_total_with_tax(99.99)
    assert result == 117.99
    result = calculate_total_with_tax(1000)
    assert result == 1180.0

# === ТЕСТЫ ДЛЯ МУТАЦИОННОГО ТЕСТИРОВАНИЯ ===

def test_discount_mutation_min_to_max():
    result = calculate_discount(1000, 30, True)
    assert result == 500

def test_discount_mutation_floor_division():
    result = calculate_discount(1000, 5, False)
    assert result == 100

def test_average_mutation_division():
    ratings = [4, 5, 3, 4]
    result = calculate_average_rating(ratings)
    assert result == 4.0
    ratings2 = [4, 5, 3, 4, 5]
    result2 = calculate_average_rating(ratings2)
    assert result2 == 4.2