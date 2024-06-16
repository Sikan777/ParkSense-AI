from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import ParkingRate, User
from src.schemas.parking import ParkingRateSchema, NewParkingRateSchema


async def create_rate(session: AsyncSession, body: ParkingRateSchema) -> ParkingRate:
    new_rate = ParkingRate(**body.model_dump(exclude_unset=True))
    session.add(new_rate)
    await session.commit()
    await session.refresh(new_rate)
    return new_rate

async def get_default_rate_values(session: AsyncSession):
    latest_rate = await session.execute(
        select(ParkingRate)
        .order_by(ParkingRate.created_at.desc())
        .limit(1)
    )
    latest_rate = latest_rate.scalars().first()
    return latest_rate

async def get_latest_rate(session: AsyncSession):
    latest_rate = await session.execute(
        select(ParkingRate)
        .order_by(ParkingRate.created_at.desc())
        .limit(1)
    )
    latest_rate = latest_rate.scalars().first()
    return latest_rate


async def create_or_update_rate(session: AsyncSession, rate_data: NewParkingRateSchema) -> ParkingRate:
    latest_rate = await session.execute(
        select(ParkingRate).order_by(ParkingRate.created_at.desc()).limit(1)
    )
    latest_rate = latest_rate.scalars().first()

    new_rate_data = {
        "rate_per_hour": rate_data.rate_per_hour if rate_data.rate_per_hour is not None else (latest_rate.rate_per_hour if latest_rate else 10.0),
        "rate_per_day": rate_data.rate_per_day if rate_data.rate_per_day is not None else (latest_rate.rate_per_day if latest_rate else 5.0),
        "number_of_spaces": rate_data.number_of_spaces if rate_data.number_of_spaces is not None else (latest_rate.number_of_spaces if latest_rate else 50),
    }

    new_rate = ParkingRate(**new_rate_data)
    session.add(new_rate)
    await session.commit()
    await session.refresh(new_rate)
    return new_rate
