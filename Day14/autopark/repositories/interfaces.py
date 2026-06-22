from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

# Используем абсолютные импорты
from autopark.models import (
    VehicleCreate, VehicleUpdate, VehicleResponse,
    TripCreate, TripResponse,
    MaintenanceCreate, MaintenanceResponse,
    DriverCreate, DriverResponse,
    GPSLocation
)


class VehicleRepository(ABC):
    """Репозиторий для работы с транспортными средствами"""
    
    @abstractmethod
    def create(self, vehicle_data: VehicleCreate) -> VehicleResponse:
        """Создать новое ТС"""
        pass
    
    @abstractmethod
    def get_by_id(self, vehicle_id: int) -> Optional[VehicleResponse]:
        """Получить ТС по ID"""
        pass
    
    @abstractmethod
    def get_by_license_plate(self, license_plate: str) -> Optional[VehicleResponse]:
        """Получить ТС по госномеру"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[VehicleResponse]:
        """Получить все ТС с пагинацией"""
        pass
    
    @abstractmethod
    def update(self, vehicle_id: int, data: VehicleUpdate) -> VehicleResponse:
        """Обновить данные ТС"""
        pass
    
    @abstractmethod
    def delete(self, vehicle_id: int) -> bool:
        """Удалить ТС (мягкое удаление)"""
        pass
    
    @abstractmethod
    def update_mileage(self, vehicle_id: int, new_mileage: int) -> VehicleResponse:
        """Обновить пробег ТС"""
        pass
    
    @abstractmethod
    def update_status(self, vehicle_id: int, status: str) -> VehicleResponse:
        """Обновить статус ТС"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[VehicleResponse]:
        """Найти ТС по статусу"""
        pass
    
    @abstractmethod
    def get_vehicles_due_for_maintenance(self, max_mileage: int) -> List[VehicleResponse]:
        """Получить ТС, требующие ТО"""
        pass
    
    @abstractmethod
    def exists(self, vehicle_id: int) -> bool:
        """Проверить существование ТС"""
        pass


class TripRepository(ABC):
    """Репозиторий для работы с поездками"""
    
    @abstractmethod
    def create(self, trip_data: TripCreate) -> TripResponse:
        """Создать новую поездку"""
        pass
    
    @abstractmethod
    def get_by_id(self, trip_id: int) -> Optional[TripResponse]:
        """Получить поездку по ID"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[TripResponse]:
        """Получить все поездки с пагинацией"""
        pass
    
    @abstractmethod
    def get_by_vehicle(self, vehicle_id: int) -> List[TripResponse]:
        """Получить поездки по ТС"""
        pass
    
    @abstractmethod
    def get_by_driver(self, driver_id: int) -> List[TripResponse]:
        """Получить поездки по водителю"""
        pass
    
    @abstractmethod
    def get_active_trips(self) -> List[TripResponse]:
        """Получить активные (незавершённые) поездки"""
        pass
    
    @abstractmethod
    def complete_trip(self, trip_id: int, end_location: str, end_time: datetime) -> TripResponse:
        """Завершить поездку"""
        pass
    
    @abstractmethod
    def exists(self, trip_id: int) -> bool:
        """Проверить существование поездки"""
        pass


class MaintenanceRepository(ABC):
    """Репозиторий для работы с ТО"""
    
    @abstractmethod
    def create(self, maintenance_data: MaintenanceCreate) -> MaintenanceResponse:
        """Создать запись о ТО"""
        pass
    
    @abstractmethod
    def get_by_id(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        """Получить запись о ТО по ID"""
        pass
    
    @abstractmethod
    def get_by_vehicle(self, vehicle_id: int) -> List[MaintenanceResponse]:
        """Получить все записи о ТО для ТС"""
        pass
    
    @abstractmethod
    def get_upcoming_maintenance(self, vehicle_id: int) -> List[MaintenanceResponse]:
        """Получить предстоящие ТО"""
        pass
    
    @abstractmethod
    def complete_maintenance(self, maintenance_id: int, completed_date: date, completed_mileage: int) -> MaintenanceResponse:
        """Завершить ТО"""
        pass
    
    @abstractmethod
    def exists(self, maintenance_id: int) -> bool:
        """Проверить существование записи"""
        pass


class DriverRepository(ABC):
    """Репозиторий для работы с водителями"""
    
    @abstractmethod
    def create(self, driver_data: DriverCreate) -> DriverResponse:
        """Создать нового водителя"""
        pass
    
    @abstractmethod
    def get_by_id(self, driver_id: int) -> Optional[DriverResponse]:
        """Получить водителя по ID"""
        pass
    
    @abstractmethod
    def get_by_license(self, license_number: str) -> Optional[DriverResponse]:
        """Получить водителя по номеру прав"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[DriverResponse]:
        """Получить всех водителей с пагинацией"""
        pass
    
    @abstractmethod
    def update(self, driver_id: int, data: DriverCreate) -> DriverResponse:
        """Обновить данные водителя"""
        pass
    
    @abstractmethod
    def delete(self, driver_id: int) -> bool:
        """Удалить водителя"""
        pass
    
    @abstractmethod
    def get_active_drivers(self) -> List[DriverResponse]:
        """Получить активных водителей"""
        pass
    
    @abstractmethod
    def exists(self, driver_id: int) -> bool:
        """Проверить существование водителя"""
        pass


class GPSRepository(ABC):
    """Репозиторий для работы с GPS данными"""
    
    @abstractmethod
    def save_location(self, location: GPSLocation) -> None:
        """Сохранить GPS координаты"""
        pass
    
    @abstractmethod
    def get_latest_location(self, vehicle_id: int) -> Optional[GPSLocation]:
        """Получить последние координаты ТС"""
        pass
    
    @abstractmethod
    def get_locations_in_period(self, vehicle_id: int, start_time: datetime, end_time: datetime) -> List[GPSLocation]:
        """Получить координаты за период"""
        pass