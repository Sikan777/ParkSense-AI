from typing import Optional, Union
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class ParkingRateUpdate(BaseModel):
    """Pydantic model for validating incoming ParkingRate data for updating."""
    rate_per_hour: float
    rate_per_day: float
    number_of_spaces: int = Field(default=50, nullable=True)
    number_free_spaces: int
    history: Union[UUID, int]


class NewParkingRateSchema(BaseModel):
    """Pydantic model for validating incoming ParkingRate data."""
    rate_per_hour: Optional[float] = None
    rate_per_day: Optional[float] = None
    number_of_spaces: Optional[int] = None


class ParkingRateSchema(BaseModel):
    """Pydantic model for validating incoming ParkingRate data."""
    rate_per_hour: float
    rate_per_day: float
    number_of_spaces: int = Field(default=50, nullable=True)


class ParkingRateResponse(BaseModel):
    """Pydantic model for serializing ParkingRate data in responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    rate_per_hour: float
    rate_per_day: float
    number_of_spaces: int = Field(default=50, nullable=True)
    
    
