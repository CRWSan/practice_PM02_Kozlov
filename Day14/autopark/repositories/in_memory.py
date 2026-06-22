from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict

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
    GPSLocation
)
from autopark.exceptions import NotFoundError


class InMemoryVehicleRepository(VehicleRepository):
    def __init__(self):
        self._vehicles: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._license_plate_to_id: Dict[str, int] = {}

    def _to_response(self, data: Dict[str, Any]) -> VehicleResponse:
        return VehicleResponse(
            id=data['id'],
            license_plate=data['license_plate'],
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            fuel_type=data['fuel_type'],
            mileage=data['mileage'],
            status=data['status'],
            maintenance_interval_km=data['maintenance_interval_km'],
            last_maintenance_mileage=data['last_maintenance_mileage'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )

    def create(self, vehicle_data: VehicleCreate) -> VehicleResponse:
        vehicle_dict = vehicle_data.model_dump()
        vehicle_dict['id'] = self._next_id
        vehicle_dict['created_at'] = datetime.now()
        vehicle_dict['updated_at'] = datetime.now()
        self._vehicles[self._next_id] = vehicle_dict
        self._license_plate_to_id[vehicle_data.license_plate] = self._next_id
        self._next_id += 1
        return self._to_response(vehicle_dict)

    def get_by_id(self, vehicle_id: int) -> Optional[VehicleResponse]:
        data = self._vehicles.get(vehicle_id)
        return self._to_response(data) if data else None

    def get_by_license_plate(self, license_plate: str) -> Optional[VehicleResponse]:
        vehicle_id = self._license_plate_to_id.get(license_plate)
        if vehicle_id:
            return self.get_by_id(vehicle_id)
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[VehicleResponse]:
        items = list(self._vehicles.values())[skip:skip + limit]
        return [self._to_response(item) for item in items]

    def update(self, vehicle_id: int, data: VehicleUpdate) -> VehicleResponse:
        if vehicle_id not in self._vehicles:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        
        vehicle = self._vehicles[vehicle_id]
        update_data = data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if key == 'license_plate' and value != vehicle['license_plate']:
                del self._license_plate_to_id[vehicle['license_plate']]
                self._license_plate_to_id[value] = vehicle_id
            vehicle[key] = value
        
        vehicle['updated_at'] = datetime.now()
        return self._to_response(vehicle)

    def delete(self, vehicle_id: int) -> bool:
        if vehicle_id not in self._vehicles:
            return False
        vehicle = self._vehicles[vehicle_id]
        del self._license_plate_to_id[vehicle['license_plate']]
        del self._vehicles[vehicle_id]
        return True

    def update_mileage(self, vehicle_id: int, new_mileage: int) -> VehicleResponse:
        if vehicle_id not in self._vehicles:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        
        vehicle = self._vehicles[vehicle_id]
        if new_mileage < vehicle['mileage']:
            raise ValueError("New mileage cannot be less than current mileage")
        
        vehicle['mileage'] = new_mileage
        vehicle['updated_at'] = datetime.now()
        return self._to_response(vehicle)

    def update_status(self, vehicle_id: int, status: str) -> VehicleResponse:
        if vehicle_id not in self._vehicles:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        
        self._vehicles[vehicle_id]['status'] = status
        self._vehicles[vehicle_id]['updated_at'] = datetime.now()
        return self._to_response(self._vehicles[vehicle_id])

    def find_by_status(self, status: str) -> List[VehicleResponse]:
        result = [v for v in self._vehicles.values() if v['status'] == status]
        return [self._to_response(item) for item in result]

    def get_vehicles_due_for_maintenance(self, max_mileage: int) -> List[VehicleResponse]:
        result = [
            v for v in self._vehicles.values() 
            if v['mileage'] - v['last_maintenance_mileage'] >= max_mileage
        ]
        return [self._to_response(item) for item in result]

    def exists(self, vehicle_id: int) -> bool:
        return vehicle_id in self._vehicles


class InMemoryTripRepository(TripRepository):
    def __init__(self):
        self._trips: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def _to_response(self, data: Dict[str, Any]) -> TripResponse:
        return TripResponse(
            id=data['id'],
            vehicle_id=data['vehicle_id'],
            driver_id=data['driver_id'],
            start_location=data['start_location'],
            end_location=data['end_location'],
            distance_km=data['distance_km'],
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            is_completed=data.get('is_completed', False),
            purpose=data.get('purpose'),
            created_at=data['created_at']
        )

    def create(self, trip_data: TripCreate) -> TripResponse:
        trip_dict = trip_data.model_dump()
        trip_dict['id'] = self._next_id
        trip_dict['is_completed'] = False
        trip_dict['created_at'] = datetime.now()
        self._trips[self._next_id] = trip_dict
        self._next_id += 1
        return self._to_response(trip_dict)

    def get_by_id(self, trip_id: int) -> Optional[TripResponse]:
        data = self._trips.get(trip_id)
        return self._to_response(data) if data else None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TripResponse]:
        items = list(self._trips.values())[skip:skip + limit]
        return [self._to_response(item) for item in items]

    def get_by_vehicle(self, vehicle_id: int) -> List[TripResponse]:
        result = [t for t in self._trips.values() if t['vehicle_id'] == vehicle_id]
        return [self._to_response(item) for item in result]

    def get_by_driver(self, driver_id: int) -> List[TripResponse]:
        result = [t for t in self._trips.values() if t['driver_id'] == driver_id]
        return [self._to_response(item) for item in result]

    def get_active_trips(self) -> List[TripResponse]:
        result = [t for t in self._trips.values() if not t.get('is_completed', False)]
        return [self._to_response(item) for item in result]

    def complete_trip(self, trip_id: int, end_location: str, end_time: datetime) -> TripResponse:
        if trip_id not in self._trips:
            raise NotFoundError(f"Trip {trip_id} not found")
        
        trip = self._trips[trip_id]
        if trip.get('is_completed', False):
            raise ValueError(f"Trip {trip_id} is already completed")
        
        trip['end_location'] = end_location
        trip['end_time'] = end_time
        trip['is_completed'] = True
        return self._to_response(trip)

    def exists(self, trip_id: int) -> bool:
        return trip_id in self._trips


class InMemoryMaintenanceRepository(MaintenanceRepository):
    def __init__(self):
        self._maintenance: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def _to_response(self, data: Dict[str, Any]) -> MaintenanceResponse:
        return MaintenanceResponse(
            id=data['id'],
            vehicle_id=data['vehicle_id'],
            maintenance_type=data['maintenance_type'],
            scheduled_date=data['scheduled_date'],
            completed_date=data.get('completed_date'),
            description=data['description'],
            cost=data['cost'],
            completed_mileage=data['completed_mileage'],
            is_completed=data.get('is_completed', False),
            created_at=data['created_at']
        )

    def create(self, maintenance_data: MaintenanceCreate) -> MaintenanceResponse:
        maint_dict = maintenance_data.model_dump()
        maint_dict['id'] = self._next_id
        maint_dict['created_at'] = datetime.now()
        self._maintenance[self._next_id] = maint_dict
        self._next_id += 1
        return self._to_response(maint_dict)

    def get_by_id(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        data = self._maintenance.get(maintenance_id)
        return self._to_response(data) if data else None

    def get_by_vehicle(self, vehicle_id: int) -> List[MaintenanceResponse]:
        result = [m for m in self._maintenance.values() if m['vehicle_id'] == vehicle_id]
        return [self._to_response(item) for item in result]

    def get_upcoming_maintenance(self, vehicle_id: int) -> List[MaintenanceResponse]:
        result = [
            m for m in self._maintenance.values()
            if m['vehicle_id'] == vehicle_id and not m.get('is_completed', False)
        ]
        return [self._to_response(item) for item in result]

    def complete_maintenance(self, maintenance_id: int, completed_date: date, completed_mileage: int) -> MaintenanceResponse:
        if maintenance_id not in self._maintenance:
            raise NotFoundError(f"Maintenance {maintenance_id} not found")
        
        maint = self._maintenance[maintenance_id]
        if maint.get('is_completed', False):
            raise ValueError(f"Maintenance {maintenance_id} is already completed")
        
        maint['completed_date'] = completed_date
        maint['completed_mileage'] = completed_mileage
        maint['is_completed'] = True
        return self._to_response(maint)

    def exists(self, maintenance_id: int) -> bool:
        return maintenance_id in self._maintenance


class InMemoryDriverRepository(DriverRepository):
    def __init__(self):
        self._drivers: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        self._license_to_id: Dict[str, int] = {}

    def _to_response(self, data: Dict[str, Any]) -> DriverResponse:
        return DriverResponse(
            id=data['id'],
            name=data['name'],
            license_number=data['license_number'],
            phone=data['phone'],
            email=data.get('email'),
            hire_date=data['hire_date'],
            is_active=data.get('is_active', True),
            created_at=data['created_at']
        )

    def create(self, driver_data: DriverCreate) -> DriverResponse:
        driver_dict = driver_data.model_dump()
        driver_dict['id'] = self._next_id
        driver_dict['created_at'] = datetime.now()
        self._drivers[self._next_id] = driver_dict
        self._license_to_id[driver_data.license_number] = self._next_id
        self._next_id += 1
        return self._to_response(driver_dict)

    def get_by_id(self, driver_id: int) -> Optional[DriverResponse]:
        data = self._drivers.get(driver_id)
        return self._to_response(data) if data else None

    def get_by_license(self, license_number: str) -> Optional[DriverResponse]:
        driver_id = self._license_to_id.get(license_number)
        if driver_id:
            return self.get_by_id(driver_id)
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[DriverResponse]:
        items = list(self._drivers.values())[skip:skip + limit]
        return [self._to_response(item) for item in items]

    def update(self, driver_id: int, data: DriverCreate) -> DriverResponse:
        if driver_id not in self._drivers:
            raise NotFoundError(f"Driver {driver_id} not found")
        
        driver = self._drivers[driver_id]
        update_data = data.model_dump()
        
        if update_data['license_number'] != driver['license_number']:
            del self._license_to_id[driver['license_number']]
            self._license_to_id[update_data['license_number']] = driver_id
        
        driver.update(update_data)
        return self._to_response(driver)

    def delete(self, driver_id: int) -> bool:
        if driver_id not in self._drivers:
            return False
        driver = self._drivers[driver_id]
        del self._license_to_id[driver['license_number']]
        del self._drivers[driver_id]
        return True

    def get_active_drivers(self) -> List[DriverResponse]:
        result = [d for d in self._drivers.values() if d.get('is_active', True)]
        return [self._to_response(item) for item in result]

    def exists(self, driver_id: int) -> bool:
        return driver_id in self._drivers


class InMemoryGPSRepository(GPSRepository):
    def __init__(self):
        self._locations: Dict[int, List[GPSLocation]] = defaultdict(list)

    def save_location(self, location: GPSLocation) -> None:
        self._locations[location.vehicle_id].append(location)

    def get_latest_location(self, vehicle_id: int) -> Optional[GPSLocation]:
        locations = self._locations.get(vehicle_id, [])
        if locations:
            return max(locations, key=lambda loc: loc.timestamp)
        return None

    def get_locations_in_period(self, vehicle_id: int, start_time: datetime, end_time: datetime) -> List[GPSLocation]:
        locations = self._locations.get(vehicle_id, [])
        return [
            loc for loc in locations
            if start_time <= loc.timestamp <= end_time
        ]