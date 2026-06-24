import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
import httpx

from app.models import Order, OrderItem, OrderStatus
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


class TestOrderRepository:
    """Тесты для OrderRepository"""

    def test_create_order_success(self, repository, db_session):
        """Тест 1: Проверка успешного создания заказа и позиций"""
        # Arrange
        order_data = {
            "customer_name": "Иван Петров",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "total_amount": 2500.0,
            "status": OrderStatus.PENDING.value,
            "items": [
                {"product_name": "Ноутбук", "quantity": 1, "price": 1500.0},
                {"product_name": "Мышь", "quantity": 2, "price": 500.0},
            ]
        }
        
        # Act
        order = repository.create(order_data)
        
        # Assert
        assert order.id is not None
        assert order.customer_name == "Иван Петров"
        assert order.delivery_address == "г. Москва, ул. Тверская, д. 10"
        assert order.total_amount == 2500.0
        assert order.status == OrderStatus.PENDING.value
        assert len(order.items) == 2
        assert order.items[0].product_name == "Ноутбук"
        assert order.items[1].product_name == "Мышь"
        
        # Проверяем, что данные сохранились в БД
        saved_order = db_session.query(Order).filter(Order.id == order.id).first()
        assert saved_order is not None
        assert len(saved_order.items) == 2

    def test_find_by_id_existing(self, repository, sample_order):
        """Тест 2: Поиск существующего заказа по ID"""
        # Act
        found_order = repository.find_by_id(sample_order.id)
        
        # Assert
        assert found_order is not None
        assert found_order.id == sample_order.id
        assert found_order.customer_name == sample_order.customer_name

    def test_find_by_id_not_existing(self, repository):
        """Тест 3: Поиск несуществующего заказа"""
        # Act
        found_order = repository.find_by_id(99999)
        
        # Assert
        assert found_order is None

    @pytest.mark.parametrize("status, expected_count", [
        (OrderStatus.PENDING.value, 1),
        (OrderStatus.PAID.value, 1),
        (OrderStatus.SHIPPED.value, 1),
        (OrderStatus.CANCELLED.value, 0),
    ])
    def test_find_all_by_status(self, repository, sample_orders, status, expected_count):
        """Тест 4: Параметризованный поиск по статусу"""
        # Act
        orders = repository.find_all_by_status(status)
        
        # Assert
        assert len(orders) == expected_count
        for order in orders:
            assert order.status == status

    def test_update_status_success(self, repository, sample_order):
        """Тест 5: Успешное обновление статуса заказа"""
        # Arrange
        new_status = OrderStatus.PAID.value
        
        # Act
        updated_order = repository.update_status(sample_order.id, new_status)
        
        # Assert
        assert updated_order.id == sample_order.id
        assert updated_order.status == new_status
        
        # Проверяем, что изменилось в БД
        db_order = repository.find_by_id(sample_order.id)
        assert db_order.status == new_status

    def test_update_status_not_found(self, repository):
        """Тест 6: Обновление статуса несуществующего заказа"""
        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            repository.update_status(99999, OrderStatus.PAID.value)
        
        assert "Order with id 99999 not found" in str(exc_info.value)

    def test_delete_order(self, repository, sample_order, db_session):
        """Тест 7: Удаление заказа с каскадным удалением позиций"""
        # Импортируем модель внутри теста
        from app.models import OrderItem
        
        # Act
        order_id = sample_order.id
        repository.delete(order_id)
        
        # Assert
        deleted_order = repository.find_by_id(order_id)
        assert deleted_order is None
        
        # Проверяем, что позиции тоже удалены
        items_count = db_session.query(OrderItem).filter(OrderItem.order_id == order_id).count()
        assert items_count == 0

    def test_find_by_date_range(self, repository, sample_orders):
        """Тест 8: Поиск заказов по диапазону дат"""
        # Arrange
        now = datetime.now()
        start_date = now - timedelta(days=1.5)
        end_date = now + timedelta(days=0.5)
        
        # Act
        orders = repository.find_by_date_range(start_date, end_date)
        
        # Assert
        # Должны найтись заказы за сегодня и вчера (2 штуки)
        assert len(orders) == 2
        # Проверяем, что все заказы в диапазоне
        for order in orders:
            assert start_date <= order.created_at <= end_date

    def test_get_total_amount_for_order(self, repository, sample_order):
        """Тест 9: Подсчёт суммы заказа"""
        # Act
        total = repository.get_total_amount_for_order(sample_order.id)
        
        # Assert
        # Ожидаемая сумма: 1500 + 2 * 500 = 2500
        assert total == 2500.0

    def test_get_total_amount_for_empty_order(self, repository, db_session):
        """Тест 9b: Подсчёт суммы заказа без позиций"""
        # Arrange
        order_data = {
            "customer_name": "Тест",
            "delivery_address": "Адрес",
            "total_amount": 0.0,
            "status": OrderStatus.PENDING.value,
            "items": []
        }
        order = repository.create(order_data)
        
        # Act
        total = repository.get_total_amount_for_order(order.id)
        
        # Assert
        assert total == 0.0

    def test_transaction_rollback_on_invalid_data(self, repository, db_session):
        """Тест 10: Транзакционность - откат при некорректных данных"""
        # Arrange
        invalid_order_data = {
            "customer_name": "Иван Петров",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "total_amount": -100.0,
            "status": OrderStatus.PENDING.value,
            "items": [
                {"product_name": "Ноутбук", "quantity": -1, "price": 1500.0},
            ]
        }
        
        # Act & Assert
        try:
            repository.create(invalid_order_data)
        except Exception:
            db_session.rollback()
        
        # Проверяем, что заказов нет
        all_orders = db_session.query(Order).all()
        assert len(all_orders) == 0

    def test_calculate_delivery_cost_success(self, repository, sample_order):
        """Тест 11: Успешный расчёт стоимости доставки через внешний API"""
        # Arrange - создаём мок для httpx.Client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cost": 150.0}
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        
        # Патчим httpx.Client
        with patch('httpx.Client') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client
            
            # Act
            cost = repository.calculate_delivery_cost(sample_order.id)
            
            # Assert
            assert cost == 150.0
            
            # Проверяем, что запрос сформирован правильно
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://api.delivery.com/calculate"
            assert call_args[1]["json"]["address"] == sample_order.delivery_address
            assert call_args[1]["json"]["weight"] == 1.5  # 3 товара * 0.5 кг

    def test_calculate_delivery_cost_api_error(self, repository, sample_order):
        """Тест 12: Ошибка API при расчёте доставки"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.Client') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(DeliveryCalculationException) as exc_info:
                repository.calculate_delivery_cost(sample_order.id)
            
            assert "API returned status 500" in str(exc_info.value)

    def test_calculate_delivery_cost_network_error(self, repository, sample_order):
        """Тест 13: Сетевая ошибка при расчёте доставки"""
        # Arrange
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.RequestError("Connection failed")
        
        with patch('httpx.Client') as MockClient:
            MockClient.return_value.__enter__.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(DeliveryCalculationException) as exc_info:
                repository.calculate_delivery_cost(sample_order.id)
            
            assert "Network error occurred" in str(exc_info.value)

    def test_calculate_delivery_cost_order_not_found(self, repository):
        """Тест 14: Расчёт доставки для несуществующего заказа"""
        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            repository.calculate_delivery_cost(99999)
        
        assert "Order with id 99999 not found" in str(exc_info.value)