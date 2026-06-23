import pytest
from app.services.stock import StockService

@pytest.fixture
def stock_service():
    """Фикстура для создания сервиса с начальным запасом 5 единиц"""
    return StockService(initial_stock=5)

@pytest.fixture
def product_id():
    """Фикстура с ID товара для тестов"""
    return 1

@pytest.fixture
def reservation_amount():
    """Фикстура с количеством резервирования"""
    return 1