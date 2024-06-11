from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repository.history import add_plate, get_plate_by_number
from schemas.history import PlateCreate, Plate
from database import get_db
from src.services.auth import auth_service 
from src.entity.models import User

router = APIRouter()

@router.post("/plates/", response_model=Plate)
async def create_plate(plate: PlateCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    await add_plate(db, plate)
    db_plate = await get_plate_by_number(db, plate.plate_number)
    if db_plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return db_plate

@router.get("/plates/{plate_number}", response_model=Plate)
async def read_plate(plate_number: str, db: AsyncSession = Depends(get_db)):
    plate = await get_plate_by_number(db, plate_number)
    if plate is None:
        raise HTTPException(status_code=404, detail="Plate not found")
    return plate
