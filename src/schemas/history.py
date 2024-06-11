from pydantic import BaseModel
from datetime import datetime

class PlateBase(BaseModel):
    plate_number: str

class PlateCreate(PlateBase):
    pass

class PlateInDBBase(PlateBase):
    id: int
    registered_at: datetime

    class Config:
        orm_mode = True

class Plate(PlateInDBBase):
    pass
