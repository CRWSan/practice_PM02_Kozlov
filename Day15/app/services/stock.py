import threading
from typing import Dict
from app.exceptions import NotEnoughStockException

class StockService:
    """Сервис для управления складскими запасами с поддержкой конкурентного доступа"""
    
    def __init__(self, initial_stock: int = 0):
        """
        Инициализация сервиса
        
        Args:
            initial_stock: Начальное количество товара на складе
        """
        self.stock: Dict[int, int] = {1: initial_stock}  # product_id -> quantity
        self.lock = threading.Lock()  # Блокировка для потокобезопасности
        self._reservation_log = []  # Лог для отслеживания операций
    
    def reserve_stock(self, product_id: int, amount: int) -> bool:
        """
        Резервирование товара на складе (потокобезопасный метод)
        
        Args:
            product_id: ID товара
            amount: Количество для резервирования
            
        Returns:
            bool: True если резервация успешна
            
        Raises:
            NotEnoughStockException: Если недостаточно товара на складе
        """
        with self.lock:
            current_stock = self.stock.get(product_id, 0)
            
            if current_stock < amount:
                raise NotEnoughStockException(
                    f"Недостаточно товара. Запрошено: {amount}, доступно: {current_stock}"
                )
            
            # Уменьшаем остаток
            self.stock[product_id] = current_stock - amount
            self._reservation_log.append({
                'product_id': product_id,
                'amount': amount,
                'remaining': self.stock[product_id],
                'thread': threading.current_thread().name
            })
            return True
    
    def get_remaining(self, product_id: int) -> int:
        """
        Получение остатка товара
        
        Args:
            product_id: ID товара
            
        Returns:
            int: Количество товара на складе
        """
        return self.stock.get(product_id, 0)
    
    def get_reservation_log(self) -> list:
        """Получение лога операций резервирования"""
        return self._reservation_log.copy()