from datetime import datetime, timedelta
from typing import Sequence, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import History, ParkingRate
from src.repository.car import CarRepository

#Implementing entry time recording every time a license plate is detected
async def create_entry(find_plate: str, image_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now()
    # number_free_spaces,rate_id = await update_parking_spaces(session)
    # number_free_spaces -= 1
    

    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    image_id = int(image_id)
    if car_row:
        car_id = car_row.id
    else:

        history_new = History(entry_time=entry_time, image_id=image_id,
                              #number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
        session.add(history_new)
        await session.commit()
        await session.refresh(history_new)
        return history_new

    history_new = History(entry_time=entry_time, car_id=car_id, image_id=image_id,
                          #number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
    session.add(history_new)
    await session.commit()
    await session.refresh(history_new)
    return history_new

#Implementing exit time recording every time a license plate is detected
async def create_exit(find_plate: str, image_id: int, session: AsyncSession):
    history_entries = await get_history_entries_with_null_exit_time(session)
    # number_free_spaces, rate_id = await update_parking_spaces(session)
    # number_free_spaces += 1
    # rate_id=int(rate_id)
    image_id = int(image_id)

    exit_time = datetime.now()
    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    if car_row:
        for history in history_entries:
            if history.car_id == car_row.id:

                history.exit_time = exit_time
                # history.number_free_spaces = number_free_spaces
                # history.rate_id = rate_id

                #to the calculation of the cost of parking (using parking rate values)(class ParkingRate from the module category)
                rate_per_hour, rate_per_day = await get_parking_rates_for_date(history.entry_time, session)

                #Implementing parking duration tracking
                duration_hours = await calculate_parking_duration(history.entry_time, history.exit_time)

                #the calculation of the cost of parking
                if duration_hours > 24:
                    cost = await calculate_parking_cost(duration_hours, rate_per_day)
                else:
                    cost = await calculate_parking_cost(duration_hours, rate_per_hour)

                history.parking_time = duration_hours  #duration of parking
                history.cost = cost #the calculation of the cost of parking

                car_row.credit -= cost #the calculation of the cost of parking
                session.add(car_row)

                if car_row.credit >= 0:
                    history.paid = True #the calculation of the cost of parking

                await session.commit()
                await session.refresh(history)
                return history
    else:
        history_new = History(
            exit_time=exit_time, image_id=image_id, ###number_free_spaces=number_free_spaces,rate_id=rate_id
            )
        session.add(history_new)
        await session.commit()
        await session.refresh(history_new)
        return history_new

    return None

#Implementing parking duration tracking
async def calculate_parking_duration(entry_time: datetime, exit_time: datetime) -> float:
    duration = exit_time - entry_time
    hours = duration / timedelta(hours=1)
    return round(hours, 2)

#the calculation of the cost of parking
async def calculate_parking_cost(duration_hours: float, rate_per_hour: float) -> float:
    cost = round(duration_hours * rate_per_hour, 2)
    return cost

#to the calculation of the cost of parking (using parking rate values)(class ParkingRate from the module category)
async def get_parking_rates_for_date(entry_time: datetime, session: AsyncSession) -> Tuple[float, float]:
    rates = await session.execute(
        select(ParkingRate).filter(ParkingRate.created_at <= entry_time)
        .order_by(ParkingRate.created_at.desc()).limit(1)
    )
    rate_row = rates.scalars().first()
    if rate_row:
        return rate_row.rate_per_hour, rate_row.rate_per_day
    else:
        default_rate_per_hour = ParkingRate.rate_per_hour.default.arg
        default_rate_per_day = ParkingRate.rate_per_day.default.arg
        return default_rate_per_hour, default_rate_per_day

async def get_history_entries_with_null_exit_time(session: AsyncSession) -> Sequence[History]:

    stmt = select(History).filter(
        or_(History.exit_time.is_(None), History.exit_time == func.now()))
    result = await session.execute(stmt)
    history_entries = result.unique().scalars().all()
    return history_entries
