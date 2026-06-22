import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, date
from decimal import Decimal

# Используем абсолютные импорты
from autopark.services.autopark_service import AutoparkService
from autopark.models import (
    VehicleCreate, VehicleUpdate, VehicleStatus, FuelType,
    TripCreate, MaintenanceCreate, DriverCreate, MaintenanceType,
    MaintenanceScheduleResponse
)
from autopark.exceptions import (
    VehicleNotFoundError, DriverNotFoundError, TripNotFoundError,
    ValidationError, BusinessRuleViolation,
    VehicleUnavailableError, DriverInactiveError,
    MaintenanceOverdueError, InvalidMileageError,
    MaintenanceNotFoundError
)


@pytest.fixture
def mock_repositories():
    """Создание моков для репозиториев"""
    return {
        'vehicle': Mock(),
        'trip': Mock(),
        'maintenance': Mock(),
        'driver': Mock(),
        'gps': Mock()
    }


@pytest.fixture
def service(mock_repositories):
    """Создание сервиса с моками"""
    return AutoparkService(
        vehicle_repository=mock_repositories['vehicle'],
        trip_repository=mock_repositories['trip'],
        maintenance_repository=mock_repositories['maintenance'],
        driver_repository=mock_repositories['driver'],
        gps_repository=mock_repositories['gps']
    )


class TestVehicleManagement:
    """Тесты управления ТС"""
    
    def test_add_vehicle_success(self, service, mock_repositories):
        """Успешное добавление ТС"""
        vehicle_data = VehicleCreate(
            license_plate="A123BC",
            brand="Toyota",
            model="Camry",
            year=2020,
            fuel_type=FuelType.PETROL,
            mileage=15000,
            status=VehicleStatus.AVAILABLE,
            maintenance_interval_km=10000,
            last_maintenance_mileage=10000
        )
        
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.license_plate = "A123BC"
        
        mock_repositories['vehicle'].get_by_license_plate.return_value = None
        mock_repositories['vehicle'].create.return_value = mock_vehicle
        
        result = service.add_vehicle(vehicle_data)
        
        assert result.id == 1
        mock_repositories['vehicle'].create.assert_called_once()
    
    def test_add_vehicle_duplicate_plate(self, service, mock_repositories):
        """Ошибка при добавлении ТС с существующим госномером"""
        vehicle_data = VehicleCreate(
            license_plate="A123BC",
            brand="Toyota",
            model="Camry",
            year=2020,
            fuel_type=FuelType.PETROL,
            mileage=15000,
            status=VehicleStatus.AVAILABLE,
            maintenance_interval_km=10000,
            last_maintenance_mileage=10000
        )
        
        mock_repositories['vehicle'].get_by_license_plate.return_value = MagicMock()
        
        with pytest.raises(ValidationError, match="already exists"):
            service.add_vehicle(vehicle_data)
    
    def test_get_vehicle_not_found(self, service, mock_repositories):
        """Ошибка при получении несуществующего ТС"""
        mock_repositories['vehicle'].get_by_id.return_value = None
        
        with pytest.raises(VehicleNotFoundError):
            service.get_vehicle(999)
    
    def test_update_vehicle_mileage_success(self, service, mock_repositories):
        """Успешное обновление пробега"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.mileage = 15000
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['vehicle'].exists.return_value = True
        mock_repositories['vehicle'].update_mileage.return_value = mock_vehicle
        
        result = service.update_vehicle_mileage(1, 16000)
        
        assert result.id == 1
        mock_repositories['vehicle'].update_mileage.assert_called_with(1, 16000)
    
    def test_update_vehicle_mileage_invalid(self, service, mock_repositories):
        """Ошибка при обновлении пробега на меньшее значение"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.mileage = 15000
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        
        with pytest.raises(InvalidMileageError):
            service.update_vehicle_mileage(1, 14000)
    
    def test_delete_vehicle_with_active_trips(self, service, mock_repositories):
        """Ошибка при удалении ТС с активными поездками"""
        mock_repositories['vehicle'].exists.return_value = True
        
        mock_trip = MagicMock()
        mock_trip.is_completed = False
        mock_repositories['trip'].get_by_vehicle.return_value = [mock_trip]
        
        with pytest.raises(BusinessRuleViolation, match="active trips"):
            service.delete_vehicle(1)


class TestTripManagement:
    """Тесты управления поездками"""
    
    def test_start_trip_success(self, service, mock_repositories):
        """Успешное начало поездки"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.status = VehicleStatus.AVAILABLE
        mock_vehicle.mileage = 15000
        mock_vehicle.last_maintenance_mileage = 10000
        mock_vehicle.maintenance_interval_km = 10000
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.is_active = True
        
        mock_trip = MagicMock()
        mock_trip.id = 1
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['driver'].get_by_id.return_value = mock_driver
        mock_repositories['trip'].get_by_driver.return_value = []
        mock_repositories['trip'].create.return_value = mock_trip
        
        trip_data = TripCreate(
            vehicle_id=1,
            driver_id=1,
            start_location="Location A",
            end_location="Location B",
            distance_km=100
        )
        
        result = service.start_trip(trip_data)
        
        assert result.id == 1
        mock_repositories['vehicle'].update_status.assert_called_with(1, VehicleStatus.IN_USE)
        mock_repositories['trip'].create.assert_called_once()
    
    def test_start_trip_vehicle_unavailable(self, service, mock_repositories):
        """Ошибка при начале поездки на недоступном ТС"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.status = VehicleStatus.UNDER_MAINTENANCE
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.is_active = True
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['driver'].get_by_id.return_value = mock_driver
        
        trip_data = TripCreate(
            vehicle_id=1,
            driver_id=1,
            start_location="Location A",
            end_location="Location B",
            distance_km=100
        )
        
        with pytest.raises(VehicleUnavailableError):
            service.start_trip(trip_data)
    
    def test_start_trip_maintenance_overdue(self, service, mock_repositories):
        """Ошибка при начале поездки с просроченным ТО"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.status = VehicleStatus.AVAILABLE
        mock_vehicle.mileage = 25000
        mock_vehicle.last_maintenance_mileage = 10000
        mock_vehicle.maintenance_interval_km = 10000
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.is_active = True
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['driver'].get_by_id.return_value = mock_driver
        mock_repositories['trip'].get_by_driver.return_value = []
        
        trip_data = TripCreate(
            vehicle_id=1,
            driver_id=1,
            start_location="Location A",
            end_location="Location B",
            distance_km=100
        )
        
        with pytest.raises(MaintenanceOverdueError):
            service.start_trip(trip_data)
    
    def test_start_trip_driver_inactive(self, service, mock_repositories):
        """Ошибка при начале поездки с неактивным водителем"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.status = VehicleStatus.AVAILABLE
        mock_vehicle.mileage = 15000
        mock_vehicle.last_maintenance_mileage = 10000
        mock_vehicle.maintenance_interval_km = 10000
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.is_active = False
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['driver'].get_by_id.return_value = mock_driver
        
        trip_data = TripCreate(
            vehicle_id=1,
            driver_id=1,
            start_location="Location A",
            end_location="Location B",
            distance_km=100
        )
        
        with pytest.raises(DriverInactiveError):
            service.start_trip(trip_data)
    
    def test_start_trip_driver_has_active_trip(self, service, mock_repositories):
        """Ошибка при начале поездки с водителем, у которого уже есть активная поездка"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.status = VehicleStatus.AVAILABLE
        mock_vehicle.mileage = 15000
        mock_vehicle.last_maintenance_mileage = 10000
        mock_vehicle.maintenance_interval_km = 10000
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        mock_driver.is_active = True
        
        mock_active_trip = MagicMock()
        mock_active_trip.is_completed = False
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['driver'].get_by_id.return_value = mock_driver
        mock_repositories['trip'].get_by_driver.return_value = [mock_active_trip]
        
        trip_data = TripCreate(
            vehicle_id=1,
            driver_id=1,
            start_location="Location A",
            end_location="Location B",
            distance_km=100
        )
        
        with pytest.raises(BusinessRuleViolation, match="already has an active trip"):
            service.start_trip(trip_data)
    
    def test_complete_trip_success(self, service, mock_repositories):
        """Успешное завершение поездки"""
        mock_trip = MagicMock()
        mock_trip.id = 1
        mock_trip.vehicle_id = 1
        mock_trip.driver_id = 1
        mock_trip.distance_km = 100
        mock_trip.is_completed = False
        
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.mileage = 15000
        
        mock_completed_trip = MagicMock()
        mock_completed_trip.id = 1
        mock_completed_trip.is_completed = True
        
        mock_repositories['trip'].get_by_id.return_value = mock_trip
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['trip'].complete_trip.return_value = mock_completed_trip
        
        result = service.complete_trip(1, "End Location")
        
        assert result.is_completed is True
        mock_repositories['vehicle'].update_mileage.assert_called_with(1, 15100)
        mock_repositories['vehicle'].update_status.assert_called_with(1, VehicleStatus.AVAILABLE)
    
    def test_complete_trip_not_found(self, service, mock_repositories):
        """Ошибка при завершении несуществующей поездки"""
        mock_repositories['trip'].get_by_id.return_value = None
        
        with pytest.raises(TripNotFoundError):
            service.complete_trip(999, "End Location")
    
    def test_complete_trip_already_completed(self, service, mock_repositories):
        """Ошибка при завершении уже завершённой поездки"""
        mock_trip = MagicMock()
        mock_trip.id = 1
        mock_trip.is_completed = True
        
        mock_repositories['trip'].get_by_id.return_value = mock_trip
        
        with pytest.raises(BusinessRuleViolation, match="already completed"):
            service.complete_trip(1, "End Location")


class TestMaintenanceManagement:
    """Тесты управления ТО"""
    
    def test_schedule_maintenance_success(self, service, mock_repositories):
        """Успешное планирование ТО"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.mileage = 15000
        
        mock_maintenance = MagicMock()
        mock_maintenance.id = 1
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['maintenance'].create.return_value = mock_maintenance
        
        maintenance_data = MaintenanceCreate(
            vehicle_id=1,
            maintenance_type=MaintenanceType.OIL_CHANGE,
            description="Oil change",
            cost=Decimal("5000"),
            completed_mileage=15000,
            is_completed=False
        )
        
        result = service.schedule_maintenance(maintenance_data)
        
        assert result.id == 1
        mock_repositories['maintenance'].create.assert_called_once()
    
    def test_complete_maintenance_success(self, service, mock_repositories):
        """Успешное завершение ТО"""
        mock_maintenance = MagicMock()
        mock_maintenance.id = 1
        mock_maintenance.vehicle_id = 1
        mock_maintenance.is_completed = False
        
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.mileage = 15000
        
        mock_completed = MagicMock()
        mock_completed.id = 1
        mock_completed.is_completed = True
        
        mock_repositories['maintenance'].get_by_id.return_value = mock_maintenance
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['maintenance'].complete_maintenance.return_value = mock_completed
        
        result = service.complete_maintenance(1, 15000)
        
        assert result.is_completed is True
        mock_repositories['vehicle'].update.assert_called_once()
    
    def test_complete_maintenance_already_completed(self, service, mock_repositories):
        """Ошибка при завершении уже выполненного ТО"""
        mock_maintenance = MagicMock()
        mock_maintenance.id = 1
        mock_maintenance.is_completed = True
        
        mock_repositories['maintenance'].get_by_id.return_value = mock_maintenance
        
        with pytest.raises(BusinessRuleViolation, match="already completed"):
            service.complete_maintenance(1, 15000)
    
    def test_complete_maintenance_not_found(self, service, mock_repositories):
        """Ошибка при завершении несуществующего ТО"""
        mock_repositories['maintenance'].get_by_id.return_value = None
        
        with pytest.raises(MaintenanceNotFoundError):
            service.complete_maintenance(999, 15000)
    
    def test_get_vehicles_due_for_maintenance(self, service, mock_repositories):
        """Получение списка ТС, требующих ТО"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.license_plate = "A123BC"
        mock_vehicle.brand = "Toyota"
        mock_vehicle.model = "Camry"
        # Пробег значительно больше интервала ТО (просрочка на 5000 км)
        mock_vehicle.mileage = 25000
        mock_vehicle.last_maintenance_mileage = 10000
        mock_vehicle.maintenance_interval_km = 10000
        
        mock_repositories['vehicle'].get_all.return_value = [mock_vehicle]
        mock_repositories['maintenance'].get_upcoming_maintenance.return_value = []
        
        result = service.get_vehicles_due_for_maintenance()
        
        assert len(result) == 1
        assert result[0].vehicle_id == 1
        assert result[0].license_plate == "A123BC"
        # Проверяем, что километры до ТО отрицательные (просрочено на 5000 км)
        assert result[0].kilometers_until_service == -5000
        assert result[0].is_overdue is True


class TestDriverManagement:
    """Тесты управления водителями"""
    
    def test_register_driver_success(self, service, mock_repositories):
        """Успешная регистрация водителя"""
        driver_data = DriverCreate(
            name="John Doe",
            license_number="AB123456",
            phone="+79111234567",
            email="john@example.com"
        )
        
        mock_driver = MagicMock()
        mock_driver.id = 1
        
        mock_repositories['driver'].get_by_license.return_value = None
        mock_repositories['driver'].create.return_value = mock_driver
        
        result = service.register_driver(driver_data)
        
        assert result.id == 1
        mock_repositories['driver'].create.assert_called_once()
    
    def test_register_driver_duplicate_license(self, service, mock_repositories):
        """Ошибка при регистрации с существующим номером прав"""
        driver_data = DriverCreate(
            name="John Doe",
            license_number="AB123456",
            phone="+79111234567"
        )
        
        mock_repositories['driver'].get_by_license.return_value = MagicMock()
        
        with pytest.raises(ValidationError, match="already exists"):
            service.register_driver(driver_data)
    
    def test_delete_driver_with_active_trips(self, service, mock_repositories):
        """Ошибка при удалении водителя с активными поездками"""
        mock_repositories['driver'].exists.return_value = True
        
        mock_trip = MagicMock()
        mock_trip.is_completed = False
        mock_repositories['trip'].get_by_driver.return_value = [mock_trip]
        
        with pytest.raises(BusinessRuleViolation, match="active trips"):
            service.delete_driver(1)


class TestWearCalculation:
    """Тесты расчёта износа"""
    
    def test_calculate_depreciation_success(self, service, mock_repositories):
        """Успешный расчёт амортизации"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.year = 2020
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        
        result = service.calculate_depreciation(1)
        
        assert isinstance(result, Decimal)
        assert result >= Decimal('0')
    
    def test_get_vehicle_wear_success(self, service, mock_repositories):
        """Получение информации об износе"""
        mock_vehicle = MagicMock()
        mock_vehicle.id = 1
        mock_vehicle.year = 2020
        mock_vehicle.mileage = 15000
        
        mock_repositories['vehicle'].get_by_id.return_value = mock_vehicle
        mock_repositories['vehicle'].exists.return_value = True
        
        result = service.get_vehicle_wear(1)
        
        assert result['vehicle_id'] == 1
        assert 'wear_percentage' in result
        assert 'depreciation_value' in result
    
    def test_get_vehicle_wear_not_found(self, service, mock_repositories):
        """Ошибка при получении износа несуществующего ТС"""
        mock_repositories['vehicle'].exists.return_value = False
        
        with pytest.raises(VehicleNotFoundError):
            service.get_vehicle_wear(999)
    
    def test_calculate_depreciation_not_found(self, service, mock_repositories):
        """Ошибка при расчёте амортизации несуществующего ТС"""
        mock_repositories['vehicle'].get_by_id.return_value = None
        
        with pytest.raises(VehicleNotFoundError):
            service.calculate_depreciation(999)


class TestGPSIntegration:
    """Тесты GPS интеграции"""
    
    def test_update_gps_location_success(self, service, mock_repositories):
        """Успешное обновление GPS координат"""
        mock_repositories['vehicle'].exists.return_value = True
        
        service.update_gps_location(1, 55.7558, 37.6173, speed=50, heading=180)
        
        mock_repositories['gps'].save_location.assert_called_once()
    
    def test_update_gps_location_vehicle_not_found(self, service, mock_repositories):
        """Ошибка при обновлении GPS для несуществующего ТС"""
        mock_repositories['vehicle'].exists.return_value = False
        
        with pytest.raises(VehicleNotFoundError):
            service.update_gps_location(999, 55.7558, 37.6173)
    
    def test_gps_not_configured(self, service, mock_repositories):
        """Ошибка при использовании GPS без конфигурации"""
        service_without_gps = AutoparkService(
            vehicle_repository=mock_repositories['vehicle'],
            trip_repository=mock_repositories['trip'],
            maintenance_repository=mock_repositories['maintenance'],
            driver_repository=mock_repositories['driver'],
            gps_repository=None
        )
        
        with pytest.raises(BusinessRuleViolation, match="not configured"):
            service_without_gps.get_vehicle_location(1)