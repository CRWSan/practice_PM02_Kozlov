from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_SERVICE = "out_of_service"


class MaintenanceType(str, Enum):
    OIL_CHANGE = "oil_change"
    TIRE_REPLACEMENT = "tire_replacement"
    BRAKE_SERVICE = "brake_service"
    ENGINE_REPAIR = "engine_repair"
    TRANSMISSION_SERVICE = "transmission_service"
    ROUTINE_INSPECTION = "routine_inspection"
    OTHER = "other"


class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    GAS = "gas"


class VehicleCreate(BaseModel):
    license_plate: str = Field(..., min_length=1, max_length=15)
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    fuel_type: FuelType
    mileage: int = Field(..., ge=0)
    status: VehicleStatus = VehicleStatus.AVAILABLE
    maintenance_interval_km: int = Field(..., ge=1000)
    last_maintenance_mileage: int = Field(..., ge=0)

    @validator('year')
    def validate_year(cls, v):
        if v > datetime.now().year + 1:
            raise ValueError("Year cannot be in the future")
        return v

    @validator('last_maintenance_mileage')
    def validate_maintenance_mileage(cls, v, values):
        if 'mileage' in values and v > values['mileage']:
            raise ValueError("Last maintenance mileage cannot exceed current mileage")
        return v


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = Field(None, min_length=1, max_length=15)
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    fuel_type: Optional[FuelType] = None
    mileage: Optional[int] = Field(None, ge=0)
    status: Optional[VehicleStatus] = None
    maintenance_interval_km: Optional[int] = Field(None, ge=1000)
    last_maintenance_mileage: Optional[int] = Field(None, ge=0)


class VehicleResponse(BaseModel):
    id: int
    license_plate: str
    brand: str
    model: str
    year: int
    fuel_type: FuelType
    mileage: int
    status: VehicleStatus
    maintenance_interval_km: int
    last_maintenance_mileage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TripCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    start_location: str = Field(..., min_length=1)
    end_location: str = Field(..., min_length=1)
    distance_km: int = Field(..., gt=0)
    start_time: datetime = Field(default_factory=datetime.now)
    purpose: Optional[str] = None


class TripResponse(BaseModel):
    id: int
    vehicle_id: int
    driver_id: int
    start_location: str
    end_location: str
    distance_km: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_completed: bool
    purpose: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceCreate(BaseModel):
    vehicle_id: int
    maintenance_type: MaintenanceType
    scheduled_date: date = Field(default_factory=date.today)
    description: str = Field(..., min_length=1)
    cost: Decimal = Field(..., ge=0)
    completed_mileage: int = Field(..., ge=0)
    is_completed: bool = False

    @validator('completed_mileage')
    def validate_completed_mileage(cls, v, values):
        # We'll validate against actual vehicle mileage in service layer
        return v


class MaintenanceResponse(BaseModel):
    id: int
    vehicle_id: int
    maintenance_type: MaintenanceType
    scheduled_date: date
    completed_date: Optional[date] = None
    description: str
    cost: Decimal
    completed_mileage: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DriverCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    license_number: str = Field(..., min_length=1, max_length=20)
    phone: str = Field(..., min_length=1, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    hire_date: date = Field(default_factory=date.today)
    is_active: bool = True


class DriverResponse(BaseModel):
    id: int
    name: str
    license_number: str
    phone: str
    email: Optional[str]
    hire_date: date
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GPSLocation(BaseModel):
    vehicle_id: int
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: float = Field(..., ge=0)
    heading: float = Field(..., ge=0, le=360)


class MaintenanceScheduleResponse(BaseModel):
    vehicle_id: int
    license_plate: str
    brand: str
    model: str
    current_mileage: int
    next_maintenance_mileage: int
    kilometers_until_service: int
    maintenance_type: MaintenanceType
    is_overdue: bool