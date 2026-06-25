# src/calculator.py
"""
Модуль для математических расчетов в системе бронирования
"""

def calculate_discount(price: float, nights: int, is_vip: bool = False) -> float:
    if price <= 0 or nights <= 0:
        return 0.0
    base_discount = (nights // 3) * 10
    vip_bonus = 5 if is_vip else 0
    total_discount = min(base_discount + vip_bonus, 50)
    return price * (total_discount / 100)

def calculate_total_with_tax(price: float, tax_rate: float = 0.18) -> float:
    if price < 0:
        return 0.0
    result = price * (1 + tax_rate)
    return round(result, 2)

def calculate_average_rating(ratings: list) -> float:
    if not ratings:
        return 0.0
    total = sum(ratings)
    return total / len(ratings)

def is_room_available(bookings: list, check_in, check_out, room_id: int) -> bool:
    """
    Проверить доступность номера на даты.
    
    Правила:
    - День заезда (check_in) считается занятым
    - День выезда (check_out) считается свободным
    
    Пример: Бронирование с 2026-06-15 по 2026-06-18
    - Занято: 15, 16, 17
    - Свободно: 18, 19, 20
    """
    for booking in bookings:
        if booking['room_id'] != room_id:
            continue
        
        booking_check_in = booking['check_in']
        booking_check_out = booking['check_out']
        
        # Проверяем, что периоды НЕ пересекаются
        # Периоды НЕ пересекаются, если:
        # 1. check_out < booking_check_in (запрос заканчивается ДО начала бронирования)
        # 2. check_in >= booking_check_out (запрос начинается В день выезда или позже)
        if check_out < booking_check_in or check_in >= booking_check_out:
            continue  # Нет пересечения - проверяем следующее бронирование
        else:
            return False  # Есть пересечение - номер занят
    
    return True  # Нет пересечений - номер свободен