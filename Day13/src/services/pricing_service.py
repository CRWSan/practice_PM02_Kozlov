from datetime import date, timedelta
from typing import Optional

from src.domain.models import Room
from src.domain.exceptions import InvalidDatesError

class PricingService:
    """Сервис расчета стоимости с использованием стратегий"""
    
    def __init__(self, seasonal_coefficients: Optional[dict] = None):
        self.seasonal_coefficients = seasonal_coefficients or {
            6: 1.2,   # июнь
            7: 1.5,   # июль
            8: 1.5,   # август
            12: 1.3,  # декабрь (новый год)
            1: 1.1,   # январь
        }
    
    def calculate_price(
        self,
        room: Room,
        check_in: date,
        check_out: date
    ) -> float:
        """Рассчитать стоимость бронирования"""
        nights = (check_out - check_in).days
        if nights <= 0:
            raise InvalidDatesError("Количество ночей должно быть больше 0")
        
        # Базовая цена с учетом сезонности
        total = 0.0
        current_date = check_in
        
        # Подсчет стоимости по дням с учетом сезонных коэффициентов
        day_count = 0
        while day_count < nights:
            current = check_in + timedelta(days=day_count)
            month = current.month
            coefficient = self.seasonal_coefficients.get(month, 1.0)
            total += room.price_per_night * coefficient
            day_count += 1
        
        # Дополнительная скидка за длительное бронирование
        if nights >= 7:
            total *= 0.95  # 5% скидка
        if nights >= 14:
            total *= 0.9  # дополнительная скидка (всего 14.5%)
        
        return round(total, 2)