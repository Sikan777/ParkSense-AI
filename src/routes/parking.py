from src.services.auth import auth_service
from src.entity.models import User, ParkingRate
from src.database.db import get_db
from src.repository import history as repositories_history
from src.repository import parking as repositories_parking
from src.schemas.parking import ParkingRateSchema, ParkingRateResponse, NewParkingRateSchema

from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/parking-rate", tags=["Parking-Rate"])


@router.get("/free-spaces", response_model=str)
async def get_latest_parking_rate_with_free_spaces(
       user: User = Depends(auth_service.get_current_admin),
       session: AsyncSession = Depends(get_db)
):
   return await repositories_history.get_latest_parking_rate_with_free_spaces(session)


@router.post("/new-parking-rate", response_model=ParkingRateResponse, status_code=status.HTTP_201_CREATED)
async def create_rate(
        body: NewParkingRateSchema,
        user: User = Depends(auth_service.get_current_admin),
        session: AsyncSession = Depends(get_db)
):
    try:
        new_rate = await repositories_parking.create_rate(session, body)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The request is malformed')
    return new_rate




