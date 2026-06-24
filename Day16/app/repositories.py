from datetime import datetime
from typing import List, Optional, Dict, Any
import httpx

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import Order, OrderItem, OrderStatus
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


class OrderRepository:
    """Репозиторий для управления заказами"""
    def __init__(self, session: Session):
        self.session = session

    def create(self, order_data: Dict[str, Any]) -> Order:
        """
        Создаёт заказ и связанные позиции из словаря order_data
        """
        items_data = order_data.pop('items', [])
        total_amount = order_data.get('total_amount', 0.0)
        
        order = Order(**order_data)
        order.total_amount = total_amount
        
        for item_data in items_data:
            item = OrderItem(**item_data)
            order.items.append(item)
        
        self.session.add(order)
        self.session.flush()
        self.session.commit()
        
        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Возвращает заказ по ID или None"""
        return self.session.query(Order).filter(Order.id == order_id).first()

    def find_all_by_status(self, status: str) -> List[Order]:
        """Возвращает список заказов с указанным статусом"""
        return self.session.query(Order).filter(Order.status == status).all()

    def update_status(self, order_id: int, new_status: str) -> Order:
        """Обновляет статус заказа"""
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException("Order", order_id)
        
        order.status = new_status
        self.session.commit()
        return order

    def delete(self, order_id: int) -> None:
        """Жёстко удаляет заказ и все его позиции из БД"""
        order = self.find_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Возвращает заказы в указанном временном интервале"""
        return self.session.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

    def get_total_amount_for_order(self, order_id: int) -> float:
        """Вычисляет сумму всех позиций заказа"""
        result = self.session.query(
            func.sum(OrderItem.quantity * OrderItem.price).label('total')
        ).filter(OrderItem.order_id == order_id).first()
        
        return result.total if result.total is not None else 0.0

    def calculate_delivery_cost(self, order_id: int) -> float:
        """
        Рассчитывает стоимость доставки через внешний API
        """
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException("Order", order_id)
        
        total_weight = 0.0
        for item in order.items:
            total_weight += item.quantity * 0.5
        
        payload = {
            "address": order.delivery_address,
            "weight": total_weight
        }
        
        try:
            # Используем контекстный менеджер
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    "https://api.delivery.com/calculate",
                    json=payload
                )
                
                if response.status_code >= 400:
                    raise DeliveryCalculationException(
                        f"API returned status {response.status_code}"
                    )
                
                data = response.json()
                return float(data.get("cost", 0.0))
                
        except httpx.RequestError as e:
            raise DeliveryCalculationException(
                "Network error occurred",
                original_error=e
            )
        except (KeyError, ValueError) as e:
            raise DeliveryCalculationException(
                "Invalid response format",
                original_error=e
            )