from src.services import auth
from src.entity.models import User
from src.database.db import get_db
from src.repository import history as repositories_history

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/parking-rate", tags=["Parking-Rate"])


@router.get("/free-spaces", response_model=str)
async def get_latest_parking_rate_with_free_spaces(
        #user: User = Depends(auth.get_current_admin),
        session: AsyncSession = Depends(get_db)
):
    return await repositories_history.get_latest_parking_rate_with_free_spaces(session)