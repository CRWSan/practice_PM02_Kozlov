class DomainError(Exception):
    """Базовое исключение для доменных ошибок"""
    pass

class NotFoundError(DomainError):
    """Объект не найден"""
    pass

class VehicleNotFoundError(NotFoundError):
    def __init__(self, vehicle_id: int):
        super().__init__(f"Vehicle with id {vehicle_id} not found")

class DriverNotFoundError(NotFoundError):
    def __init__(self, driver_id: int):
        super().__init__(f"Driver with id {driver_id} not found")

class TripNotFoundError(NotFoundError):
    def __init__(self, trip_id: int):
        super().__init__(f"Trip with id {trip_id} not found")

class MaintenanceNotFoundError(NotFoundError):
    def __init__(self, maintenance_id: int):
        super().__init__(f"Maintenance record with id {maintenance_id} not found")

class ValidationError(DomainError):
    """Ошибка валидации данных"""
    pass

class BusinessRuleViolation(DomainError):
    """Нарушение бизнес-правила"""
    pass

class VehicleUnavailableError(BusinessRuleViolation):
    def __init__(self, vehicle_id: int, status: str):
        super().__init__(f"Vehicle {vehicle_id} is not available for trip (status: {status})")

class DriverInactiveError(BusinessRuleViolation):
    def __init__(self, driver_id: int):
        super().__init__(f"Driver {driver_id} is not active")

class MaintenanceOverdueError(BusinessRuleViolation):
    def __init__(self, vehicle_id: int, overdue_km: int):
        super().__init__(f"Vehicle {vehicle_id} is overdue for maintenance by {overdue_km} km")

class TripAlreadyCompletedError(BusinessRuleViolation):
    def __init__(self, trip_id: int):
        super().__init__(f"Trip {trip_id} is already completed")

class InvalidMileageError(ValidationError):
    def __init__(self, message: str):
        super().__init__(f"Invalid mileage: {message}")

class GPSDataError(DomainError):
    """Ошибка получения данных GPS"""
    pass