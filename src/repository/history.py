from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert
from src.entity.models import Car, History


async def add_plate(session: AsyncSession, plate: str, model: str):
    stmt = insert(Car).values(plate=plate, model=model)
    await session.execute(stmt)
    await session.commit()

async def get_car_by_plate(session: AsyncSession, plate: str):
    result = await session.execute(select(Car).where(Car.plate == plate))
    return result.scalars().first()
