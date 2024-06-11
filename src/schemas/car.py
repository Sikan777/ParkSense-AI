from typing import Optional, Union, List

from pydantic import BaseModel, Field


class CarModel(BaseModel):
    credit: Optional[float]
    plate: str
    model: Optional[str]
    user_ids: List[int] = Field(default_factory=list)


class CarUpdate(BaseModel):
    credit: Optional[float] = None
    plate: Optional[str] = None
    model: Optional[str] = None
    ban: bool = Field(default=False, nullable=True)
    user_ids: Optional[List[int]] = None


class NewCarResponse(BaseModel):
    id: int
    credit: Optional[float]
    plate: str
    model: Optional[str]
    ban: Optional[bool]
    user_ids: List[int] = Field(default_factory=list)

    class Config:
        from_attributes = True
