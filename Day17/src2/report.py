from typing import List, Dict, Optional
from datetime import datetime, timedelta


def generate_booking_report(bookings: List[Dict]) -> Dict:
    """Генерирует отчет по списку бронирований"""
    if not bookings:
        return {
            'total_bookings': 0,
            'average_price': 0,
            'status_counts': {},
            'total_revenue': 0,
            'most_popular_hotel': None
        }
    
    total_bookings = len(bookings)
    
    # ИСПРАВЛЕНО: Проверка на нулевые цены
    prices = [b.get('price', 0) for b in bookings if b.get('price', 0) > 0]
    total_price = sum(prices)
    average_price = total_price / len(prices) if prices else 0
    
    # Подсчет статусов
    status_counts = {}
    for b in bookings:
        status = b.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # ИСПРАВЛЕНО: Учитываем только подтвержденные бронирования для выручки
    total_revenue = sum(b.get('price', 0) for b in bookings if b.get('status') == 'confirmed')
    
    # Поиск самого популярного отеля
    hotel_counts = {}
    for b in bookings:
        hotel = b.get('hotel_name', '')
        if hotel:
            hotel_counts[hotel] = hotel_counts.get(hotel, 0) + 1
    
    most_popular_hotel = max(hotel_counts, key=hotel_counts.get) if hotel_counts else None
    
    return {
        'total_bookings': total_bookings,
        'average_price': average_price,
        'status_counts': status_counts,
        'total_revenue': total_revenue,
        'most_popular_hotel': most_popular_hotel
    }


def calculate_weekly_statistics(bookings: List[Dict]) -> Dict:
    """Рассчитывает статистику по дням недели"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    stats = {day: {'count': 0, 'revenue': 0, 'average': 0} for day in days}
    
    # Список поддерживаемых форматов дат
    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']
    
    for booking in bookings:
        try:
            check_in_str = booking.get('check_in', '')
            if not check_in_str:
                continue
            
            # ИСПРАВЛЕНО: Пробуем парсить дату в разных форматах
            check_in = None
            for fmt in date_formats:
                try:
                    check_in = datetime.strptime(check_in_str, fmt)
                    break
                except ValueError:
                    continue
            
            if check_in is None:
                continue
                
            day_name = check_in.strftime('%A')
            stats[day_name]['count'] += 1
            stats[day_name]['revenue'] += booking.get('price', 0)
            
        except (KeyError, ValueError):
            continue
    
    # Расчет средних значений
    for day in days:
        if stats[day]['count'] > 0:
            stats[day]['average'] = stats[day]['revenue'] / stats[day]['count']
        else:
            stats[day]['average'] = 0
    
    return stats


def generate_hotel_statistics(bookings: List[Dict]) -> Dict:
    """Генерирует статистику по отелям"""
    if not bookings:
        return {}
    
    hotel_stats = {}
    
    for booking in bookings:
        hotel_name = booking.get('hotel_name')
        if not hotel_name:
            continue
            
        if hotel_name not in hotel_stats:
            hotel_stats[hotel_name] = {
                'total_bookings': 0,
                'total_revenue': 0,
                'average_rating': 0,
                'ratings': []
            }
        
        hotel_stats[hotel_name]['total_bookings'] += 1
        hotel_stats[hotel_name]['total_revenue'] += booking.get('price', 0)
        
        rating = booking.get('rating')
        if rating is not None:
            hotel_stats[hotel_name]['ratings'].append(rating)
    
    # ИСПРАВЛЕНО: Безопасный расчет среднего рейтинга
    for hotel in hotel_stats:
        ratings = hotel_stats[hotel]['ratings']
        if ratings:
            hotel_stats[hotel]['average_rating'] = sum(ratings) / len(ratings)
        else:
            hotel_stats[hotel]['average_rating'] = 0
    
    # ИСПРАВЛЕНО: Добавлен расчет заполняемости
    for hotel in hotel_stats:
        total_bookings = hotel_stats[hotel]['total_bookings']
        # Предполагаем, что у отеля 100 номеров (для примера)
        hotel_stats[hotel]['occupancy_rate'] = min(total_bookings / 100 * 100, 100)
    
    return hotel_stats


def calculate_growth_rate(bookings: List[Dict], period_days: int = 30) -> float:
    """Рассчитывает темп роста бронирований за указанный период"""
    if not bookings:
        return 0.0
    
    now = datetime.now()
    cutoff = now - timedelta(days=period_days)
    
    current_period = []
    previous_period = []
    
    # Список поддерживаемых форматов дат
    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']
    
    for booking in bookings:
        try:
            check_in_str = booking.get('check_in', '')
            if not check_in_str:
                continue
            
            # ИСПРАВЛЕНО: Пробуем парсить дату в разных форматах
            check_in = None
            for fmt in date_formats:
                try:
                    check_in = datetime.strptime(check_in_str, fmt)
                    break
                except ValueError:
                    continue
            
            if check_in is None:
                continue
            
            # ИСПРАВЛЕНО: Правильная фильтрация по датам
            if check_in >= cutoff:
                current_period.append(booking)
            else:
                previous_period.append(booking)
        except (KeyError, ValueError):
            continue
    
    current_count = len(current_period)
    previous_count = len(previous_period)
    
    # Обработка деления на ноль
    if previous_count == 0:
        return 100.0 if current_count > 0 else 0.0
    
    # Правильная формула расчета
    growth_rate = ((current_count - previous_count) / previous_count) * 100
    
    return growth_rate