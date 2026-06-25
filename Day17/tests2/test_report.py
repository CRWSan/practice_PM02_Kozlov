import pytest
from datetime import datetime, timedelta
from src2.report import (
    generate_booking_report,
    calculate_weekly_statistics,
    generate_hotel_statistics,
    calculate_growth_rate
)


# ========== Дополнительные тесты для generate_booking_report ==========

def test_generate_booking_report_with_zero_prices():
    """Тест с нулевыми ценами"""
    bookings = [
        {'price': 0, 'status': 'confirmed', 'hotel_name': 'Hilton'},
        {'price': 100, 'status': 'confirmed', 'hotel_name': 'Marriott'},
    ]
    
    result = generate_booking_report(bookings)
    
    # Средняя должна считаться только по положительным ценам
    assert result['average_price'] == 100.0
    assert result['total_revenue'] == 100  # Только confirmed


def test_generate_booking_report_with_cancelled():
    """Тест с отмененными бронированиями"""
    bookings = [
        {'price': 100, 'status': 'confirmed', 'hotel_name': 'Hilton'},
        {'price': 200, 'status': 'cancelled', 'hotel_name': 'Marriott'},
    ]
    
    result = generate_booking_report(bookings)
    
    # Выручка должна учитывать только confirmed
    assert result['total_revenue'] == 100
    assert result['status_counts']['confirmed'] == 1
    assert result['status_counts']['cancelled'] == 1


# ========== Дополнительные тесты для calculate_weekly_statistics ==========

def test_calculate_weekly_statistics_with_invalid_dates():
    """Тест с некорректными датами"""
    bookings = [
        {'check_in': 'invalid-date', 'price': 100},
        {'check_in': '2026-06-15', 'price': 200},
    ]
    
    result = calculate_weekly_statistics(bookings)
    
    # Некорректная дата должна быть пропущена
    assert result['Monday']['count'] == 1  # Только валидная запись


def test_calculate_weekly_statistics_all_days():
    """Тест с бронированиями на все дни недели"""
    bookings = []
    base_date = datetime(2026, 6, 15)  # Monday
    
    for i in range(7):
        date = base_date + timedelta(days=i)
        bookings.append({'check_in': date.strftime('%Y-%m-%d'), 'price': 100})
    
    result = calculate_weekly_statistics(bookings)
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        assert result[day]['count'] == 1
        assert result[day]['revenue'] == 100
        assert result[day]['average'] == 100.0


# ========== Дополнительные тесты для generate_hotel_statistics ==========

def test_generate_hotel_statistics_with_empty_ratings():
    """Тест с отелями без рейтингов"""
    bookings = [
        {'hotel_name': 'Hilton', 'price': 100},
        {'hotel_name': 'Hilton', 'price': 150},
    ]
    
    result = generate_hotel_statistics(bookings)
    
    assert result['Hilton']['average_rating'] == 0
    assert result['Hilton']['total_bookings'] == 2


def test_generate_hotel_statistics_occupancy():
    """Тест расчета заполняемости"""
    bookings = [{'hotel_name': 'Hilton', 'price': 100} for _ in range(50)]
    
    result = generate_hotel_statistics(bookings)
    
    assert result['Hilton']['occupancy_rate'] == 50.0  # 50 из 100 номеров


# ========== Дополнительные тесты для calculate_growth_rate ==========

def test_calculate_growth_rate_decline():
    """Тест с отрицательным ростом (спад)"""
    now = datetime.now()
    old_date = now - timedelta(days=40)
    new_date = now - timedelta(days=10)
    
    bookings = []
    for _ in range(10):  # 10 старых
        bookings.append({'check_in': old_date.strftime('%Y-%m-%d')})
    for _ in range(5):   # 5 новых
        bookings.append({'check_in': new_date.strftime('%Y-%m-%d')})
    
    result = calculate_growth_rate(bookings, 30)
    
    # Ожидается: (5 - 10) / 10 * 100 = -50%
    assert result == -50.0


def test_calculate_growth_rate_no_current():
    """Тест когда нет текущих бронирований"""
    now = datetime.now()
    old_date = now - timedelta(days=40)
    
    bookings = [
        {'check_in': old_date.strftime('%Y-%m-%d')},
        {'check_in': old_date.strftime('%Y-%m-%d')},
    ]
    
    result = calculate_growth_rate(bookings, 30)
    
    assert result == -100.0  # (0 - 2) / 2 * 100 = -100%


def test_calculate_growth_rate_with_different_formats():
    """Тест с разными форматами дат"""
    now = datetime.now()
    new_date = now - timedelta(days=10)
    
    bookings = [
        {'check_in': new_date.strftime('%d/%m/%Y')},  # DD/MM/YYYY
        {'check_in': new_date.strftime('%m/%d/%Y')},  # MM/DD/YYYY
    ]
    
    result = calculate_growth_rate(bookings, 30)
    
    # Должны быть обработаны оба формата
    assert result == 100.0  # 2 новых, 0 старых


def test_calculate_growth_rate_with_multiple_formats():
    """Тест с разными форматами дат в одном наборе данных"""
    now = datetime.now()
    new_date = now - timedelta(days=10)
    old_date = now - timedelta(days=40)
    
    bookings = [
        {'check_in': new_date.strftime('%Y-%m-%d')},    # YYYY-MM-DD
        {'check_in': new_date.strftime('%d/%m/%Y')},    # DD/MM/YYYY
        {'check_in': new_date.strftime('%m/%d/%Y')},    # MM/DD/YYYY
        {'check_in': old_date.strftime('%Y-%m-%d')},    # Старая дата
        {'check_in': old_date.strftime('%d/%m/%Y')},    # Старая дата
    ]
    
    result = calculate_growth_rate(bookings, 30)
    
    # 3 новых, 2 старых: (3-2)/2 * 100 = 50%
    assert result == 50.0


def test_calculate_weekly_statistics_with_multiple_formats():
    """Тест статистики с разными форматами дат"""
    bookings = [
        {'check_in': '15/06/2026', 'price': 100},   # DD/MM/YYYY
        {'check_in': '06/16/2026', 'price': 200},   # MM/DD/YYYY
        {'check_in': '2026-06-17', 'price': 150},   # YYYY-MM-DD
    ]
    
    result = calculate_weekly_statistics(bookings)
    
    # Все даты должны быть распаршены корректно
    total_count = sum(result[day]['count'] for day in result)
    assert total_count == 3
    assert result['Monday']['count'] == 1  # 15/06/2026 - Monday
    assert result['Tuesday']['count'] == 1  # 06/16/2026 - Tuesday
    assert result['Wednesday']['count'] == 1  # 2026-06-17 - Wednesday


def test_calculate_growth_rate_with_invalid_format():
    """Тест с невалидным форматом даты"""
    now = datetime.now()
    new_date = now - timedelta(days=10)
    
    bookings = [
        {'check_in': new_date.strftime('%Y-%m-%d')},
        {'check_in': 'invalid-date-format'},
        {'check_in': new_date.strftime('%d/%m/%Y')},
    ]
    
    result = calculate_growth_rate(bookings, 30)
    
    # Должны быть обработаны только валидные даты (2 из 3)
    assert result == 100.0  # 2 новых, 0 старых


def test_calculate_weekly_statistics_with_invalid_format():
    """Тест статистики с невалидным форматом даты"""
    bookings = [
        {'check_in': '2026-06-15', 'price': 100},
        {'check_in': 'invalid-date', 'price': 200},
        {'check_in': '16/06/2026', 'price': 150},
    ]
    
    result = calculate_weekly_statistics(bookings)
    
    # Должны быть обработаны только валидные даты (2 из 3)
    total_count = sum(result[day]['count'] for day in result)
    assert total_count == 2
    assert result['Monday']['count'] == 1  # 2026-06-15 - Monday
    assert result['Tuesday']['count'] == 1  # 16/06/2026 - Tuesday
    