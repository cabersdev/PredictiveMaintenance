from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Union
import re

class MachineBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    name: str = Field(..., min_length=1, max_length=255, description="Machine name")
    location: str = Field(..., min_length=1, max_length=255, description="Machine location")
    hours: float = Field(..., ge=0, description="Total operating hours")
    degrade: float = Field(..., ge=0, le=1.0, description="Degradation factor (0-1)")
    fault_threshold: float = Field(..., ge=0, le=1.0, description="Fault threshold (0-1)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9\-_ ]+$', v):
            raise ValueError('The name can only contain letters, numbers, spaces, hyphens and underscores')
        return v.strip()

    @model_validator(mode='after')
    def validate_consistency(self) -> 'MachineBase':
        # A machine can have high degradation even with few hours (e.g. intensive use)
        # But if it has > 10000 hours, the degradation should be > 0.2 (warning soft)
        if self.hours > 10000 and self.degrade < 0.2:
            # This is a warning, not an error. In production you would log it.
            pass
        return self


class MachineCreateInput(MachineBase):
    """Input to create a new machine"""
    # Override to make created_at and updated_at optional in input
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MachineCreateOutput(MachineBase):
    """Output to create a new machine"""
    id: UUID = Field(..., description="Unique ID of the machine")


class MachineUpdateInput(BaseModel):
    """Input to update a machine (all fields are optional)"""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    hours: Optional[float] = Field(None, ge=0)
    degrade: Optional[float] = Field(None, ge=0, le=1.0)
    fault_threshold: Optional[float] = Field(None, ge=0, le=1.0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\-_ ]+$', v):
                raise ValueError('The name can only contain letters, numbers, spaces, hyphens and underscores')
            return v.strip()
        return v

    def model_dump(self, **kwargs):
        """Override to remove None fields (useful for PATCH)"""
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}


class MachineUpdateOutput(MachineBase):
    """Output to update a machine"""
    id: UUID


class MachineDeleteInput(BaseModel):
    """Input to delete a machine"""
    id: UUID = Field(..., description="ID of the machine to delete")


class MachineDeleteOutput(BaseModel):
    """Output to delete a machine"""
    message: str = Field(default="Machine deleted successfully")


class MachineGetInput(BaseModel):
    """Input to get a machine"""
    id: UUID


class MachineGetOutput(MachineBase):
    """Output to get a machine"""
    id: UUID


class MachineSummary(BaseModel):
    """Lightweight version for lists (faster)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    location: str
    degrade: float
    fault_threshold: float


class MachineListInput(BaseModel):
    """Input to list machines (optional filters)"""
    name: Optional[str] = None
    location: Optional[str] = None
    min_degrade: Optional[float] = Field(None, ge=0, le=1.0)
    max_degrade: Optional[float] = Field(None, ge=0, le=1.0)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    sort_by: Optional[str] = Field("name", description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


class MachineListOutput(BaseModel):
    """Output to list machines"""
    machines: List[MachineSummary]
    total: int
    limit: int
    offset: int