import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime
from decimal import Decimal

from autopark.models import (
    VehicleCreate, VehicleStatus, FuelType,
    TripCreate, MaintenanceCreate, MaintenanceType,
    DriverCreate
)
from autopark.repositories.in_memory import (
    InMemoryVehicleRepository,
    InMemoryTripRepository,
    InMemoryMaintenanceRepository,
    InMemoryDriverRepository,
    InMemoryGPSRepository
)
from autopark.services.autopark_service import AutoparkService
from autopark.exceptions import DomainError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Пример использования сервиса автопарка"""
    
    # Создание репозиториев
    vehicle_repo = InMemoryVehicleRepository()
    trip_repo = InMemoryTripRepository()
    maintenance_repo = InMemoryMaintenanceRepository()
    driver_repo = InMemoryDriverRepository()
    gps_repo = InMemoryGPSRepository()
    
    # Создание сервиса с внедрением зависимостей
    service = AutoparkService(
        vehicle_repository=vehicle_repo,
        trip_repository=trip_repo,
        maintenance_repository=maintenance_repo,
        driver_repository=driver_repo,
        gps_repository=gps_repo
    )
    
    print("=" * 60)
    print("АВТОПАРК - СИСТЕМА УПРАВЛЕНИЯ ТС")
    print("=" * 60)
    
    try:
        # 1. Добавление ТС
        print("\n1. Добавление ТС:")
        vehicle = service.add_vehicle(VehicleCreate(
            license_plate="A777AA",
            brand="Toyota",
            model="Land Cruiser",
            year=2022,
            fuel_type=FuelType.DIESEL,
            mileage=5000,
            status=VehicleStatus.AVAILABLE,
            maintenance_interval_km=15000,
            last_maintenance_mileage=0
        ))
        print(f"   Добавлено ТС: {vehicle.brand} {vehicle.model} ({vehicle.license_plate})")
        
        # 2. Регистрация водителя
        print("\n2. Регистрация водителя:")
        driver = service.register_driver(DriverCreate(
            name="Иван Петров",
            license_number="AA123456",
            phone="+79111234567",
            email="ivan@example.com"
        ))
        print(f"   Зарегистрирован водитель: {driver.name}")
        
        # 3. Начало поездки
        print("\n3. Начало поездки:")
        trip = service.start_trip(TripCreate(
            vehicle_id=vehicle.id,
            driver_id=driver.id,
            start_location="Москва, ул. Тверская, 1",
            end_location="Москва, ул. Арбат, 10",
            distance_km=15
        ))
        print(f"   Поездка #{trip.id} начата: {trip.start_location} -> {trip.end_location}")
        
        # 4. Обновление GPS координат
        print("\n4. Обновление GPS данных:")
        service.update_gps_location(vehicle.id, 55.7558, 37.6173, speed=40)
        location = service.get_vehicle_location(vehicle.id)
        print(f"   Текущие координаты: {location.latitude}, {location.longitude}")
        
        # 5. Завершение поездки
        print("\n5. Завершение поездки:")
        completed_trip = service.complete_trip(trip.id, "Москва, ул. Арбат, 10")
        print(f"   Поездка #{completed_trip.id} завершена")
        
        # 6. Обновление пробега
        print("\n6. Обновление пробега:")
        updated_vehicle = service.update_vehicle_mileage(vehicle.id, 5015)
        print(f"   Пробег обновлён: {updated_vehicle.mileage} км")
        
        # 7. Планирование ТО
        print("\n7. Планирование ТО:")
        maintenance = service.schedule_maintenance(MaintenanceCreate(
            vehicle_id=vehicle.id,
            maintenance_type=MaintenanceType.OIL_CHANGE,
            scheduled_date=datetime.now().date(),
            description="Замена масла и фильтров",
            cost=Decimal("7500"),
            completed_mileage=5015
        ))
        print(f"   Запланировано ТО #{maintenance.id}: {maintenance.description}")
        
        # 8. Проверка ТС, требующих ТО
        print("\n8. Проверка ТС, требующих ТО:")
        due_vehicles = service.get_vehicles_due_for_maintenance()
        if due_vehicles:
            for v in due_vehicles:
                status = "ПРОСРОЧЕНО" if v.is_overdue else "СКОРО"
                print(f"   {v.license_plate}: до ТО {v.kilometers_until_service} км ({status})")
        else:
            print("   Все ТС в норме")
        
        # 9. Расчёт износа
        print("\n9. Расчёт износа ТС:")
        wear = service.get_vehicle_wear(vehicle.id)
        print(f"   Износ: {wear['wear_percentage']}%")
        print(f"   Амортизация: {wear['depreciation_value']:.2f} руб.")
        
        print("\n" + "=" * 60)
        print("Работа завершена успешно!")
        
    except DomainError as e:
        print(f"\nОшибка: {e}")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()