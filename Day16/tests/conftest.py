import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base, Order, OrderItem, OrderStatus
from app.repositories import OrderRepository


@pytest.fixture(scope="function")
def db_session():
    """Фикстура с in-memory SQLite базой данных"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def repository(db_session: Session):
    """Фикстура для создания репозитория"""
    return OrderRepository(db_session)


@pytest.fixture
def sample_order_data():
    """Фикстура с данными для заказа"""
    return {
        "customer_name": "Иван Петров",
        "delivery_address": "г. Москва, ул. Тверская, д. 10",
        "total_amount": 2500.0,
        "status": OrderStatus.PENDING.value,
        "items": [
            {"product_name": "Ноутбук", "quantity": 1, "price": 1500.0},
            {"product_name": "Мышь", "quantity": 2, "price": 500.0},
        ]
    }


@pytest.fixture
def sample_order(repository: OrderRepository, sample_order_data: dict) -> Order:
    """Фикстура с созданным заказом"""
    return repository.create(sample_order_data)


@pytest.fixture
def sample_orders(repository: OrderRepository):
    """Фикстура с несколькими заказами"""
    base_data = {
        "customer_name": "Тестовый Клиент",
        "delivery_address": "ул. Тестовая, д. 1",
        "items": [{"product_name": "Товар", "quantity": 1, "price": 100.0}]
    }
    
    orders = []
    
    # Заказ PENDING
    data1 = base_data.copy()
    data1.update({
        "status": OrderStatus.PENDING.value,
        "total_amount": 100.0,
        "customer_name": "Клиент 1"
    })
    orders.append(repository.create(data1))
    
    # Заказ PAID
    data2 = base_data.copy()
    data2.update({
        "status": OrderStatus.PAID.value,
        "total_amount": 200.0,
        "customer_name": "Клиент 2"
    })
    order2 = repository.create(data2)
    order2.created_at = datetime.now() - timedelta(days=1)
    repository.session.commit()
    orders.append(order2)
    
    # Заказ SHIPPED
    data3 = base_data.copy()
    data3.update({
        "status": OrderStatus.SHIPPED.value,
        "total_amount": 300.0,
        "customer_name": "Клиент 3"
    })
    order3 = repository.create(data3)
    order3.created_at = datetime.now() - timedelta(days=2)
    repository.session.commit()
    orders.append(order3)
    
    return orders