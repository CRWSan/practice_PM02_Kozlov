from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, 
    Enum, CheckConstraint, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

Base = declarative_base()


class OrderStatus(str, enum.Enum):
    """Статусы заказа"""
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """Модель заказа"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default=OrderStatus.PENDING.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=func.now()
    )
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    delivery_address: Mapped[str] = mapped_column(String(200), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Отношение один-ко-многим с позициями заказа
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status={self.status}, customer={self.customer_name})>"


class OrderItem(Base):
    """Модель позиции заказа"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # Обратная связь с заказом
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    # Ограничение: количество должно быть положительным
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price >= 0', name='check_price_non_negative'),
    )

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product={self.product_name}, qty={self.quantity})>"