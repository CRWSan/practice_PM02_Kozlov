import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

# Используем абсолютные импорты
from autopark.repositories.interfaces import (
    VehicleRepository, TripRepository,
    MaintenanceRepository, DriverRepository, GPSRepository
)
from autopark.models import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleStatus,
    TripCreate, TripResponse,
    MaintenanceCreate, MaintenanceResponse,
    DriverCreate, DriverResponse,
    GPSLocation,
    MaintenanceScheduleResponse
)
from autopark.exceptions import (
    VehicleNotFoundError, DriverNotFoundError, TripNotFoundError,
    MaintenanceNotFoundError,
    ValidationError, BusinessRuleViolation,
    VehicleUnavailableError, DriverInactiveError,
    MaintenanceOverdueError, TripAlreadyCompletedError,
    InvalidMileageError
)

logger = logging.getLogger(__name__)


class AutoparkService:
    """
    Основной сервис для управления автопарком.
    
    Отвечает за:
    - Управление ТС (CRUD, обновление пробега, статуса)
    - Управление водителями (CRUD)
    - Управление поездками (создание, завершение)
    - Управление ТО (создание, завершение)
    - Расчёт износа ТС
    - Интеграция с GPS
    """
    
    def __init__(
        self,
        vehicle_repository: VehicleRepository,
        trip_repository: TripRepository,
        maintenance_repository: MaintenanceRepository,
        driver_repository: DriverRepository,
        gps_repository: Optional[GPSRepository] = None
    ):
        self._vehicles = vehicle_repository
        self._trips = trip_repository
        self._maintenance = maintenance_repository
        self._drivers = driver_repository
        self._gps = gps_repository
        
        # Конфигурационные параметры
        self._maintenance_threshold_km = 1000  # Порог для предупреждения о ТО
        self._depreciation_rate = 0.15  # Годовая норма амортизации (15%)
        self._max_mileage_per_day = 500  # Максимальный пробег в день
        
        logger.info("AutoparkService initialized")

    # ========== Управление транспортными средствами ==========
    
    def add_vehicle(self, vehicle_data: VehicleCreate) -> VehicleResponse:
        """Добавить новое ТС"""
        logger.info(f"Adding new vehicle: {vehicle_data.license_plate}")
        
        # Проверка на дубликат госномера
        existing = self._vehicles.get_by_license_plate(vehicle_data.license_plate)
        if existing:
            raise ValidationError(f"Vehicle with license plate {vehicle_data.license_plate} already exists")
        
        # Валидация пробега
        if vehicle_data.mileage < vehicle_data.last_maintenance_mileage:
            raise InvalidMileageError(
                f"Current mileage ({vehicle_data.mileage}) cannot be less than "
                f"last maintenance mileage ({vehicle_data.last_maintenance_mileage})"
            )
        
        vehicle = self._vehicles.create(vehicle_data)
        logger.info(f"Vehicle added with id {vehicle.id}")
        return vehicle
    
    def get_vehicle(self, vehicle_id: int) -> VehicleResponse:
        """Получить ТС по ID"""
        vehicle = self._vehicles.get_by_id(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(vehicle_id)
        return vehicle
    
    def get_vehicle_by_plate(self, license_plate: str) -> VehicleResponse:
        """Получить ТС по госномеру"""
        vehicle = self._vehicles.get_by_license_plate(license_plate)
        if not vehicle:
            raise ValidationError(f"Vehicle with license plate {license_plate} not found")
        return vehicle
    
    def get_all_vehicles(self, skip: int = 0, limit: int = 100) -> List[VehicleResponse]:
        """Получить все ТС"""
        return self._vehicles.get_all(skip, limit)
    
    def update_vehicle(self, vehicle_id: int, data: VehicleUpdate) -> VehicleResponse:
        """Обновить данные ТС"""
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        # Проверка дубликата госномера при обновлении
        if data.license_plate:
            existing = self._vehicles.get_by_license_plate(data.license_plate)
            if existing and existing.id != vehicle_id:
                raise ValidationError(f"License plate {data.license_plate} already in use")
        
        return self._vehicles.update(vehicle_id, data)
    
    def delete_vehicle(self, vehicle_id: int) -> bool:
        """Удалить ТС"""
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        # Проверка наличия активных поездок
        trips = self._trips.get_by_vehicle(vehicle_id)
        active_trips = [t for t in trips if not t.is_completed]
        if active_trips:
            raise BusinessRuleViolation(
                f"Cannot delete vehicle with {len(active_trips)} active trips"
            )
        
        logger.info(f"Deleting vehicle {vehicle_id}")
        return self._vehicles.delete(vehicle_id)
    
    def update_vehicle_mileage(self, vehicle_id: int, new_mileage: int) -> VehicleResponse:
        """Обновить пробег ТС"""
        vehicle = self._vehicles.get_by_id(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(vehicle_id)
        
        if new_mileage < vehicle.mileage:
            raise InvalidMileageError(
                f"New mileage ({new_mileage}) cannot be less than current mileage ({vehicle.mileage})"
            )
        
        # Проверка превышения дневного лимита пробега
        daily_mileage = new_mileage - vehicle.mileage
        if daily_mileage > self._max_mileage_per_day:
            logger.warning(f"Vehicle {vehicle_id} exceeded daily mileage limit: {daily_mileage} km")
        
        logger.info(f"Updating mileage for vehicle {vehicle_id}: {vehicle.mileage} -> {new_mileage}")
        return self._vehicles.update_mileage(vehicle_id, new_mileage)

    # ========== Управление водителями ==========
    
    def register_driver(self, driver_data: DriverCreate) -> DriverResponse:
        """Зарегистрировать нового водителя"""
        logger.info(f"Registering new driver: {driver_data.name}")
        
        # Проверка дубликата номера прав
        existing = self._drivers.get_by_license(driver_data.license_number)
        if existing:
            raise ValidationError(f"Driver with license {driver_data.license_number} already exists")
        
        return self._drivers.create(driver_data)
    
    def get_driver(self, driver_id: int) -> DriverResponse:
        """Получить водителя по ID"""
        driver = self._drivers.get_by_id(driver_id)
        if not driver:
            raise DriverNotFoundError(driver_id)
        return driver
    
    def get_all_drivers(self, skip: int = 0, limit: int = 100) -> List[DriverResponse]:
        """Получить всех водителей"""
        return self._drivers.get_all(skip, limit)
    
    def update_driver(self, driver_id: int, data: DriverCreate) -> DriverResponse:
        """Обновить данные водителя"""
        if not self._drivers.exists(driver_id):
            raise DriverNotFoundError(driver_id)
        
        # Проверка дубликата номера прав
        existing = self._drivers.get_by_license(data.license_number)
        if existing and existing.id != driver_id:
            raise ValidationError(f"License {data.license_number} already in use")
        
        return self._drivers.update(driver_id, data)
    
    def delete_driver(self, driver_id: int) -> bool:
        """Удалить водителя"""
        if not self._drivers.exists(driver_id):
            raise DriverNotFoundError(driver_id)
        
        # Проверка наличия активных поездок
        trips = self._trips.get_by_driver(driver_id)
        active_trips = [t for t in trips if not t.is_completed]
        if active_trips:
            raise BusinessRuleViolation(
                f"Cannot delete driver with {len(active_trips)} active trips"
            )
        
        logger.info(f"Deleting driver {driver_id}")
        return self._drivers.delete(driver_id)

    # ========== Управление поездками ==========
    
    def start_trip(self, trip_data: TripCreate) -> TripResponse:
        """Начать новую поездку"""
        logger.info(f"Starting trip: vehicle {trip_data.vehicle_id}, driver {trip_data.driver_id}")
        
        # Проверка ТС
        vehicle = self._vehicles.get_by_id(trip_data.vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(trip_data.vehicle_id)
        
        # Проверка доступности ТС
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise VehicleUnavailableError(trip_data.vehicle_id, vehicle.status)
        
        # Проверка водителя
        driver = self._drivers.get_by_id(trip_data.driver_id)
        if not driver:
            raise DriverNotFoundError(trip_data.driver_id)
        
        if not driver.is_active:
            raise DriverInactiveError(trip_data.driver_id)
        
        # Проверка необходимости ТО
        km_since_maintenance = vehicle.mileage - vehicle.last_maintenance_mileage
        if km_since_maintenance > vehicle.maintenance_interval_km:
            raise MaintenanceOverdueError(
                trip_data.vehicle_id,
                km_since_maintenance - vehicle.maintenance_interval_km
            )
        
        # Проверка, что водитель не ведёт другую активную поездку
        active_trips = self._trips.get_by_driver(trip_data.driver_id)
        if any(not t.is_completed for t in active_trips):
            raise BusinessRuleViolation(
                f"Driver {trip_data.driver_id} already has an active trip"
            )
        
        # Обновление статуса ТС
        self._vehicles.update_status(trip_data.vehicle_id, VehicleStatus.IN_USE)
        
        # Создание поездки
        trip = self._trips.create(trip_data)
        
        logger.info(f"Trip started with id {trip.id}")
        return trip
    
    def complete_trip(self, trip_id: int, end_location: str) -> TripResponse:
        """Завершить поездку"""
        logger.info(f"Completing trip {trip_id}")
        
        trip = self._trips.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError(trip_id)
        
        if trip.is_completed:
            raise TripAlreadyCompletedError(trip_id)
        
        # Обновление пробега ТС
        vehicle = self._vehicles.get_by_id(trip.vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(trip.vehicle_id)
        
        new_mileage = vehicle.mileage + trip.distance_km
        self._vehicles.update_mileage(trip.vehicle_id, new_mileage)
        
        # Обновление статуса ТС
        self._vehicles.update_status(trip.vehicle_id, VehicleStatus.AVAILABLE)
        
        # Завершение поездки
        completed_trip = self._trips.complete_trip(
            trip_id, 
            end_location, 
            datetime.now()
        )
        
        logger.info(f"Trip {trip_id} completed")
        return completed_trip
    
    def get_trip_history(self, vehicle_id: int) -> List[TripResponse]:
        """Получить историю поездок для ТС"""
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        return self._trips.get_by_vehicle(vehicle_id)
    
    def get_active_trips(self) -> List[TripResponse]:
        """Получить активные поездки"""
        return self._trips.get_active_trips()

    # ========== Управление ТО ==========
    
    def schedule_maintenance(self, maintenance_data: MaintenanceCreate) -> MaintenanceResponse:
        """Запланировать ТО"""
        logger.info(f"Scheduling maintenance for vehicle {maintenance_data.vehicle_id}")
        
        vehicle = self._vehicles.get_by_id(maintenance_data.vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(maintenance_data.vehicle_id)
        
        # Проверка пробега при завершённом ТО
        if maintenance_data.is_completed:
            if maintenance_data.completed_mileage > vehicle.mileage:
                raise InvalidMileageError(
                    f"Completed mileage ({maintenance_data.completed_mileage}) "
                    f"cannot exceed current mileage ({vehicle.mileage})"
                )
        
        return self._maintenance.create(maintenance_data)
    
    def complete_maintenance(self, maintenance_id: int, completed_mileage: int) -> MaintenanceResponse:
        """Завершить ТО"""
        logger.info(f"Completing maintenance {maintenance_id}")
        
        maintenance = self._maintenance.get_by_id(maintenance_id)
        if not maintenance:
            raise MaintenanceNotFoundError(maintenance_id)
        
        if maintenance.is_completed:
            raise BusinessRuleViolation(f"Maintenance {maintenance_id} already completed")
        
        vehicle = self._vehicles.get_by_id(maintenance.vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(maintenance.vehicle_id)
        
        if completed_mileage > vehicle.mileage:
            raise InvalidMileageError(
                f"Completed mileage ({completed_mileage}) cannot exceed "
                f"current mileage ({vehicle.mileage})"
            )
        
        # Обновление пробега ТО в ТС
        self._vehicles.update(maintenance.vehicle_id, VehicleUpdate(
            last_maintenance_mileage=completed_mileage
        ))
        
        # Обновление статуса ТС, если был на ТО
        if vehicle.status == VehicleStatus.UNDER_MAINTENANCE:
            self._vehicles.update_status(maintenance.vehicle_id, VehicleStatus.AVAILABLE)
        
        completed = self._maintenance.complete_maintenance(
            maintenance_id,
            date.today(),
            completed_mileage
        )
        
        logger.info(f"Maintenance {maintenance_id} completed")
        return completed
    
    def get_vehicles_due_for_maintenance(self) -> List[MaintenanceScheduleResponse]:
        """Получить список ТС, требующих ТО"""
        result = []
        vehicles = self._vehicles.get_all()
        
        for vehicle in vehicles:
            km_since_maintenance = vehicle.mileage - vehicle.last_maintenance_mileage
            if km_since_maintenance >= vehicle.maintenance_interval_km - self._maintenance_threshold_km:
                # Находим ближайшее запланированное ТО
                upcoming = self._maintenance.get_upcoming_maintenance(vehicle.id)
                maint_type = upcoming[0].maintenance_type if upcoming else "routine_inspection"
                
                is_overdue = km_since_maintenance >= vehicle.maintenance_interval_km
                
                result.append(MaintenanceScheduleResponse(
                    vehicle_id=vehicle.id,
                    license_plate=vehicle.license_plate,
                    brand=vehicle.brand,
                    model=vehicle.model,
                    current_mileage=vehicle.mileage,
                    next_maintenance_mileage=vehicle.last_maintenance_mileage + vehicle.maintenance_interval_km,
                    kilometers_until_service=vehicle.maintenance_interval_km - km_since_maintenance,
                    maintenance_type=maint_type,
                    is_overdue=is_overdue
                ))
        
        return result

    # ========== Расчёт износа ==========
    
    def calculate_depreciation(self, vehicle_id: int) -> Decimal:
        """
        Рассчитать амортизацию ТС.
        Используется линейный метод.
        """
        vehicle = self._vehicles.get_by_id(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(vehicle_id)
        
        # Условная стоимость ТС (для примера)
        base_price = Decimal('1000000')
        age = datetime.now().year - vehicle.year
        
        depreciation = base_price * Decimal(str(self._depreciation_rate)) * Decimal(str(age))
        return max(Decimal('0'), base_price - depreciation)
    
    def get_vehicle_wear(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Получить информацию об износе ТС
        """
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        vehicle = self._vehicles.get_by_id(vehicle_id)
        
        # Расчёт износа на основе пробега
        expected_mileage_per_year = 20000
        age = datetime.now().year - vehicle.year
        expected_mileage = age * expected_mileage_per_year
        
        wear_percentage = min(100, (vehicle.mileage / max(1, expected_mileage)) * 100)
        
        return {
            "vehicle_id": vehicle_id,
            "current_mileage": vehicle.mileage,
            "age_years": age,
            "expected_mileage": expected_mileage,
            "wear_percentage": round(wear_percentage, 2),
            "depreciation_value": float(self.calculate_depreciation(vehicle_id))
        }

    # ========== GPS интеграция ==========
    
    def update_gps_location(self, vehicle_id: int, latitude: float, longitude: float, 
                           speed: float = 0, heading: float = 0) -> None:
        """Обновить GPS координаты ТС"""
        if not self._gps:
            raise BusinessRuleViolation("GPS tracking is not configured")
        
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        location = GPSLocation(
            vehicle_id=vehicle_id,
            timestamp=datetime.now(),
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading
        )
        
        self._gps.save_location(location)
        logger.debug(f"GPS updated for vehicle {vehicle_id}")
    
    def get_vehicle_location(self, vehicle_id: int) -> Optional[GPSLocation]:
        """Получить текущее местоположение ТС"""
        if not self._gps:
            raise BusinessRuleViolation("GPS tracking is not configured")
        
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        return self._gps.get_latest_location(vehicle_id)
    
    def get_vehicle_track(self, vehicle_id: int, start_time: datetime, end_time: datetime) -> List[GPSLocation]:
        """Получить трек ТС за период"""
        if not self._gps:
            raise BusinessRuleViolation("GPS tracking is not configured")
        
        if not self._vehicles.exists(vehicle_id):
            raise VehicleNotFoundError(vehicle_id)
        
        return self._gps.get_locations_in_period(vehicle_id, start_time, end_time)