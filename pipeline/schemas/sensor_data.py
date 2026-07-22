from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional
import re

class SensorDataBase(BaseModel):
    """
        Sensor data coming from the simulator (Kafka)
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    machine_id: UUID = Field(..., description="Machine ID")
    timestamp: datetime = Field(..., description="Timestamp of the reading (UTC)")
    temperature: float = Field(..., description="Temperature in °C")
    vibration: float = Field(..., ge=0, description="Vibration in mm/s (RMS)")
    pressure: float = Field(..., ge=0, description="Pressure in bar")
    current: float = Field(..., ge=0, description="Current in A")
    hours: float = Field(..., ge=0, description="Total operating hours of the machine")
    is_fault: bool = Field(False, description="True if a fault occurred at this instant")

    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Realistic range for industrial machines"""
        if not (-50 <= v <= 300):
            raise ValueError(f'Temperature must be between -50 and 300 °C (got {v})')
        return round(v, 2)

    @field_validator('vibration')
    @classmethod
    def validate_vibration(cls, v: float) -> float:
        """Realistic range for vibrations"""
        if not (0 <= v <= 50):
            raise ValueError(f'Vibration must be between 0 and 50 mm/s (got {v})')
        return round(v, 2)

    @field_validator('pressure')
    @classmethod
    def validate_pressure(cls, v: float) -> float:
        """Realistic range for industrial pressures"""
        if not (0 <= v <= 200):
            raise ValueError(f'Pressure must be between 0 and 200 bar (got {v})')
        return round(v, 2)

    @field_validator('current')
    @classmethod
    def validate_current(cls, v: float) -> float:
        """Realistic range for industrial currents"""
        if not (0 <= v <= 500):
            raise ValueError(f'Current must be between 0 and 500 A (got {v})')
        return round(v, 2)

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """The timestamp cannot be in the future (tolerance 5 seconds)"""
        now = datetime.now(timezone.utc)
        if v > now:
            # Allow a small offset for unsynchronized clocks
            if (v - now).total_seconds() > 5:
                raise ValueError(f'Timestamp cannot be more than 5 seconds in the future (got {v})')
        return v

    @field_validator('hours')
    @classmethod
    def validate_hours(cls, v: float) -> float:
        """Hours cannot be negative"""
        if v < 0:
            raise ValueError(f'Hours cannot be negative (got {v})')
        return round(v, 1)
    
    @model_validator(mode='after')
    def validate_consistency(self) -> 'SensorDataBase':
        """
        Validations that involve multiple fields
        """
        # 1. If there is a fault, the values may be anomalous (but not an error)
        # 2. If hours is 0, the machine has never worked - it may be a new record
        # 3. High temperature (> 100°C) with low vibration (< 1 mm/s) is suspicious
        if self.temperature > 100 and self.vibration < 1.0 and not self.is_fault:
            # This is a warning, not an error. In production you would log it.
            pass
        
        return self


class SensorDataCreate(SensorDataBase):
    """Input to insert a single raw record (via API or Kafka)"""
    pass


class SensorDataOutput(SensorDataBase):
    """Output for a raw record (with ID)"""
    id: UUID = Field(..., description="Unique ID of the record")


class SensorDataBatchInput(BaseModel):
    """Input to insert a batch of raw data (from the simulator)"""
    model_config = ConfigDict(extra="forbid")
    
    records: List[SensorDataCreate] = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="List of records to insert"
    )
    
    @field_validator('records')
    @classmethod
    def validate_records(cls, v: List[SensorDataCreate]) -> List[SensorDataCreate]:
        if not v:
            raise ValueError('At least one record is required')
        return v


class SensorDataBatchOutput(BaseModel):
    """Output for batch insertion"""
    inserted: int = Field(..., description="Number of records inserted")
    failed: int = Field(0, description="Number of records failed")
    errors: List[dict] = Field(default=[], description="Error details")


class SensorDataListInput(BaseModel):
    """Input to list raw data (filters)"""
    machine_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_fault: Optional[bool] = None
    limit: int = Field(100, ge=1, le=10000)
    offset: int = Field(0, ge=0)
    sort_by: str = Field("timestamp", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class SensorDataListOutput(BaseModel):
    """Output to list raw data"""
    records: List[SensorDataOutput]
    total: int
    limit: int
    offset: int
