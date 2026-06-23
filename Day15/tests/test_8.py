import threading
import pytest
from app.services.stock import StockService
from app.exceptions import NotEnoughStockException

class TestConcurrentReservation:
    """
    Тесты для проверки конкурентного резервирования товара
    Вариант 8: Тестирование конкурентного доступа (ThreadPool)
    """
    
    def test_concurrent_reservation_basic(self):
        """
        Базовый тест конкурентного резервирования
        
        Arrange:
            - Создаем StockService с initial_stock=5
            - Подготавливаем счетчик исключений с блокировкой
            - Создаем 10 потоков для резервирования по 1 единице
        
        Act:
            - Запускаем все потоки параллельно
            - Ожидаем завершения всех потоков
        
        Assert:
            - Ровно 5 потоков должны получить исключение NotEnoughStockException
            - Остаток на складе должен стать 0
        """
        # Arrange
        stock_service = StockService(initial_stock=5)
        product_id = 1
        amount = 1
        num_threads = 10
        exception_count = 0
        exception_lock = threading.Lock()
        success_count = 0
        success_lock = threading.Lock()
        
        def reserve():
            """Функция резервирования для запуска в потоке"""
            nonlocal exception_count, success_count
            try:
                stock_service.reserve_stock(product_id, amount)
                with success_lock:
                    success_count += 1
            except NotEnoughStockException:
                with exception_lock:
                    exception_count += 1
        
        # Act
        threads = [threading.Thread(target=reserve) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Assert
        assert exception_count == 5, f"Ожидалось 5 исключений, получено {exception_count}"
        assert success_count == 5, f"Ожидалось 5 успешных операций, получено {success_count}"
        assert stock_service.get_remaining(product_id) == 0, "Остаток должен быть 0"
    
    def test_concurrent_reservation_with_different_amounts(self):
        """
        Тест с разными количествами резервирования
        
        Проверяет, что система корректно обрабатывает запросы с разными объемами
        """
        # Arrange
        stock_service = StockService(initial_stock=10)
        product_id = 1
        operations = [3, 3, 2, 2, 1]  # 5 операций, всего 11 единиц
        expected_success = 4  # Первые 4 операции должны пройти (3+3+2+2=10)
        expected_failures = 1  # Последняя операция должна упасть
        
        exception_count = 0
        success_count = 0
        exception_lock = threading.Lock()
        success_lock = threading.Lock()
        
        def reserve(amount):
            nonlocal exception_count, success_count
            try:
                stock_service.reserve_stock(product_id, amount)
                with success_lock:
                    success_count += 1
            except NotEnoughStockException:
                with exception_lock:
                    exception_count += 1
        
        # Act
        threads = [threading.Thread(target=reserve, args=(amount,)) 
                  for amount in operations]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Assert
        assert success_count == expected_success, \
            f"Ожидалось {expected_success} успешных операций, получено {success_count}"
        assert exception_count == expected_failures, \
            f"Ожидалось {expected_failures} исключений, получено {exception_count}"
        assert stock_service.get_remaining(product_id) == 0
    
    def test_concurrent_reservation_thread_safety(self):
        """
        Проверка потокобезопасности через логирование
        
        Убеждаемся, что конкурентные операции не приводят к гонкам данных
        """
        # Arrange
        stock_service = StockService(initial_stock=5)
        product_id = 1
        num_threads = 10
        #CRW
        def reserve():
            try:
                stock_service.reserve_stock(product_id, 1)
            except NotEnoughStockException:
                pass
        
        # Act
        threads = [threading.Thread(target=reserve) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Assert
        log = stock_service.get_reservation_log()
        assert len(log) == 5, f"Должно быть 5 записей в логе, получено {len(log)}"
        
        # Проверяем, что остатки в логе монотонно убывают
        remainings = [entry['remaining'] for entry in log]
        assert remainings == [4, 3, 2, 1, 0] or remainings == sorted(remainings, reverse=True), \
            f"Остатки должны монотонно убывать: {remainings}"
        
        # Проверяем, что каждый поток использовал уникальное имя (разные потоки)
        thread_names = set(entry['thread'] for entry in log)
        assert len(thread_names) == 5, "Должно быть 5 уникальных потоков"
    
    def test_concurrent_reservation_stress(self):
        """
        Стресс-тест с большим количеством потоков
        
        Проверяет работу системы при высокой нагрузке
        """
        # Arrange
        stock_service = StockService(initial_stock=100)
        product_id = 1
        num_threads = 50
        amount_per_thread = 2  # 50 * 2 = 100, все должны пройти
        
        exception_count = 0
        exception_lock = threading.Lock()
        
        def reserve():
            nonlocal exception_count
            try:
                stock_service.reserve_stock(product_id, amount_per_thread)
            except NotEnoughStockException:
                with exception_lock:
                    exception_count += 1
        
        # Act
        threads = [threading.Thread(target=reserve) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Assert
        assert exception_count == 0, f"Не должно быть исключений, получено {exception_count}"
        assert stock_service.get_remaining(product_id) == 0, "Остаток должен быть 0"
    
    @pytest.mark.parametrize("initial_stock, num_threads, amount_per_thread, expected_success, expected_failures, expected_remaining", [
        (5, 10, 1, 5, 5, 0),
        (10, 8, 2, 5, 3, 0),
        (3, 6, 1, 3, 3, 0),
        (20, 10, 3, 6, 4, 2),  # 6 * 3 = 18, остаток 2
        (15, 7, 2, 7, 0, 1),   # 7 * 2 = 14, остаток 1
    ])
    def test_concurrent_reservation_parametrized(
        self, 
        initial_stock: int, 
        num_threads: int, 
        amount_per_thread: int,
        expected_success: int,
        expected_failures: int,
        expected_remaining: int
    ):
        """
        Параметризованный тест для проверки различных сценариев
    
        Args:
            initial_stock: Начальный остаток на складе
            num_threads: Количество потоков
            amount_per_thread: Количество резервирования в каждом потоке
            expected_success: Ожидаемое количество успешных операций
            expected_failures: Ожидаемое количество неудачных операций
            expected_remaining: Ожидаемый остаток на складе
        """
        # Arrange
        stock_service = StockService(initial_stock=initial_stock)
        product_id = 1
        exception_count = 0
        success_count = 0
        exception_lock = threading.Lock()
        success_lock = threading.Lock()
    
        def reserve():
            nonlocal exception_count, success_count
            try:
                stock_service.reserve_stock(product_id, amount_per_thread)
                with success_lock:
                    success_count += 1
            except NotEnoughStockException:
                with exception_lock:
                    exception_count += 1
    
        # Act
        threads = [threading.Thread(target=reserve) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    
        # Assert
        assert success_count == expected_success, \
            f"Ожидалось {expected_success} успешных операций, получено {success_count}"
        assert exception_count == expected_failures, \
            f"Ожидалось {expected_failures} исключений, получено {exception_count}"
        assert stock_service.get_remaining(product_id) == expected_remaining, \
            f"Ожидался остаток {expected_remaining}, получено {stock_service.get_remaining(product_id)}"