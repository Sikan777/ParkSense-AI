from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.car import CarRepository
from src.repository.parking import create_rate, create_or_update_rate, get_default_rate_values
from src.schemas.user import UserResponse
from src.schemas.car import CarModel, CarUpdate, NewCarResponse
from src.schemas.parking import ParkingRateSchema, NewParkingRateSchema
from src.services.auth import auth_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/cars", response_model=NewCarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(car_data: CarModel, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    new_car = await car_repository.add_car(car_data)
    return new_car


# All users are allowed to call
@router.get("/default-parking-rate", response_model=ParkingRateSchema)
async def get_default_parking_rate(db: AsyncSession = Depends(get_db)):
    latest_rate = await get_default_rate_values(db)
    if not latest_rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rates found")
    return latest_rate


@router.post("/parking-rates", response_model=NewParkingRateSchema, status_code=status.HTTP_201_CREATED)
async def create_or_update_parking_rate(rate_data: NewParkingRateSchema, db: AsyncSession = Depends(get_db),
                                        admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    if not rate_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rate data")
    new_rate = await create_or_update_rate(db, rate_data)
    return new_rate


@router.get("/cars/parked", response_model=list[NewCarResponse], status_code=status.HTTP_200_OK)
async def read_parked_cars(db: AsyncSession = Depends(get_db),
                           admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    parked_cars = await car_repository.get_cars_currently_parked()
    if not parked_cars:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cars currently parked")
    return parked_cars


@router.get("/cars/{plate}", response_model=NewCarResponse, status_code=status.HTTP_200_OK)
async def read_car(plate: str, db: AsyncSession = Depends(get_db),
                   admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    car = await car_repository.get_car_by_plate(plate)
    if car is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return car


@router.get("/cars", response_model=list[NewCarResponse], status_code=status.HTTP_200_OK)
async def read_cars(db: AsyncSession = Depends(get_db),
                    admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    cars = await car_repository.get_all_cars()
    if cars is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cars found")
    return cars


@router.get("/users-by-car/{plate}", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def read_users_by_car(plate: str, db: AsyncSession = Depends(get_db),
                            admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    users = await car_repository.get_users_by_car_plate(plate)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users


@router.patch("/cars/{plate}", response_model=NewCarResponse, status_code=status.HTTP_200_OK)
async def update_car(plate: str, car_update: CarUpdate, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")

    car_repository = CarRepository(db)
    updated_car = await car_repository.update_car(plate, car_update)
    return updated_car


@router.patch("/cars/{plate}/ban", response_model=dict, status_code=status.HTTP_200_OK)
async def ban_car(plate: str, db: AsyncSession = Depends(get_db),
                  admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    car = await car_repository.ban_car(plate)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    elif car:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Car {plate} has been banned"})


@router.delete("/cars/{plate}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_car(plate: str, db: AsyncSession = Depends(get_db),
                     admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You don't have enough rights")
    car_repository = CarRepository(db)
    if not await car_repository.check_car_exists(plate):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    await car_repository.delete_car(plate)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Car {plate} has been deleted"})
