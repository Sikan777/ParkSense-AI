import csv
from datetime import datetime, time, timedelta
from typing import Sequence, Tuple
from sqlalchemy import and_, desc, func, null, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Car, History, ParkingRate, User
from src.repository.car import CarRepository
from src.services.email_sender import send_email

#Implementing entry time recording every time a license plate is detected
async def create_entry(find_plate: str, image_id: int, session: AsyncSession) -> History:
    entry_time = datetime.now()
    number_free_spaces, rate_id = await update_parking_spaces(session)
    number_free_spaces -= 1
    

    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    image_id = int(image_id)
    if car_row:
        car_id = car_row.id
    else:

        history_new = History(entry_time=entry_time, image_id=image_id,
                              number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
        session.add(history_new)
        await session.commit()
        await session.refresh(history_new)
        return history_new

    history_new = History(entry_time=entry_time, car_id=car_id, image_id=image_id,
                          number_free_spaces=number_free_spaces, rate_id=rate_id,
                      exit_time=None)
    session.add(history_new)
    await session.commit()
    await session.refresh(history_new)
    return history_new

#Implementing exit time recording every time a license plate is detected
async def create_exit(find_plate: str, image_id: int, session: AsyncSession):
    history_entries = await get_history_entries_with_null_exit_time(session)
    number_free_spaces, rate_id = await update_parking_spaces(session)
    number_free_spaces += 1
    rate_id=int(rate_id)
    image_id = int(image_id)

    exit_time = datetime.now()
    car_repository = CarRepository(session)
    car_row = await car_repository.get_car_by_plate(find_plate)
    if car_row:
        for history in history_entries:
            if history.car_id == car_row.id:

                history.exit_time = exit_time
                history.number_free_spaces = number_free_spaces
                history.rate_id = rate_id

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


#Getting and adding information about paid parking
async def update_paid_history( plate: str,  paid: bool, session: AsyncSession):
    statement = select(History).where(
        and_(History.car.has(plate=plate), History.paid == False)
    )
    result = await session.execute(statement)
    history_entry = result.unique().scalars().first()

    if history_entry is None:
        return None

    history_entry.paid = paid

    await session.commit()
    await session.refresh(history_entry)
    return history_entry

#Getting information about unpaid parking
async def get_history_entries_with_null_paid(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.paid == False)
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries


###Additional functionality for getting different information
async def get_history_entries_by_period(start_time: datetime, end_time: datetime, session: AsyncSession) -> Sequence[History]:

    start_time = datetime.combine(start_time.date(), time.min)
    end_time = datetime.combine(end_time.date(), time.max)

    query = select(History).join(Car).filter(
        History.entry_time.between(start_time, end_time)
    )
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries 


async def get_history_entries_by_period_car (start_time: datetime, end_time: datetime, car_id: int, session: AsyncSession) -> Sequence[History]:
    start_time = datetime.combine(start_time.date(), time.min)
    end_time = datetime.combine(end_time.date(), time.max)

    query = select(History).join(Car).filter(
        History.entry_time.between(start_time, end_time),
        History.car_id == car_id
    )
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries

async def get_history_entries_with_null_car_id(session: AsyncSession) -> Sequence[History]:
    query = select(History).filter(History.car_id == null())
    result = await session.execute(query)
    history_entries = result.unique().scalars().all()
    return history_entries

async def update_parking_spaces(session: AsyncSession) -> Tuple[int, int]:
    history_entries = await get_history_entries_with_null_exit_time(session)
    num_entries = len(history_entries)

    latest_parking_rate = await get_latest_parking_rate(session)
    latest_parking_rate_spaces = latest_parking_rate.number_of_spaces if latest_parking_rate else 0

    number_free_spaces = latest_parking_rate_spaces - num_entries

    if number_free_spaces == 0:
        number_free_spaces = 100
    rate_id = latest_parking_rate.id if latest_parking_rate else 0
    return number_free_spaces, latest_parking_rate.id

async def get_latest_parking_rate(session: AsyncSession):
    query = select(ParkingRate).order_by(desc(ParkingRate.created_at)).limit(1)
    result = await session.execute(query)
    parking_rate = result.unique().scalar_one_or_none()
    return parking_rate


async def get_latest_parking_rate_with_free_spaces(session: AsyncSession):
    query = select(History).order_by(desc(History.created_at)).limit(1)
    result = await session.execute(query)
    latest_entry = result.unique().scalar_one_or_none()
    if latest_entry:
        return f"free spaces -  {latest_entry.number_free_spaces}"
    return "No data available"

async def update_car_history( plate: str, car_id: int, session: AsyncSession):
    statement = select(History).where(
        and_(History.image.has(current_plate=plate), History.car_id == null())
    )
    result = await session.execute(statement)
    history_entry = result.unique().scalars().first()

    if history_entry is None:
        return None

    history_entry.car_id = car_id

    await session.commit()
    await session.refresh(history_entry)
    return history_entry


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    return f"{days}d {hours}h {minutes}m"

async def save_history_to_csv(history_entries: Sequence[History], file_path: str):
    fieldnames = [
        'entry_time',
        'exit_time',
        'parking_time',
        'cost',
        'paid',
        'number_free_spaces',
        'plate'
    ]

    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in history_entries:
            parking_duration = timedelta(hours=entry.parking_time) if entry.parking_time is not None else None
            entry_dict = {
                'entry_time': entry.entry_time.strftime('%Y-%m-%d %H:%M') if entry.entry_time else None,
                'exit_time': entry.exit_time.strftime('%Y-%m-%d %H:%M') if entry.exit_time else None,
                'parking_time': format_timedelta(parking_duration) if parking_duration else None,
                'cost': f"{entry.cost:.2f}" if entry.cost is not None else None,
                'paid': entry.paid,
                'number_free_spaces': entry.number_free_spaces,
                'plate': entry.car.plate
            }
            writer.writerow(entry_dict)


### Limits of parking expenses with notification
# async def check_expense_limits(user_id: int, session: AsyncSession):
#     stmt = select(History).filter(History.car_id == user_id)
#     result = await session.execute(stmt)
#     histories = result.scalars().all()

#     total_expense = sum(history.cost for history in histories if history.paid)
    
#     limit_stmt = select(ExpenseLimit).filter(ExpenseLimit.user_id == user_id)
#     limit_result = await session.execute(limit_stmt)
#     limit = limit_result.scalars().first()
    
#     if limit and total_expense > limit.limit_amount:
#         if not limit.notification_sent:
#             await send_notification(user_id, total_expense, limit.limit_amount)
#             limit.notification_sent = True
#             await session.commit()

async def calculate_total_parking_cost(user_id: int, session: AsyncSession) -> float:
    total_cost = await session.execute(
        select(func.sum(History.cost)).where(History.car_id == Car.id, Car.user_id == user_id)
    )
    return total_cost.scalar() or 0.0

async def check_parking_limit_and_notify(user_id: int, session: AsyncSession):
    user = await session.get(User, user_id)
    if not user:
        return

    total_cost = await calculate_total_parking_cost(user_id, session)
    if total_cost > user.parking_expenses_limit:
        await send_notification(user.email, total_cost, user.parking_limit)

async def send_notification(email: str, total_cost: float, limit: float):
    subject = "Parking Expense Limit Exceeded"
    message = f"Your current parking expenses amount to {total_cost}, which exceeds the established limit {limit}."
    send_email(email, subject, message)
    
###SEND EMAIL example SMTPLIB

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# async def send_email(to_email: str, subject: str, body: str):
#     from_email = "your_email@example.com"
#     from_password = "your_email_password"
#     smtp_server = "smtp.example.com"
#     smtp_port = 587

#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject

#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(from_email, from_password)
#         server.sendmail(from_email, to_email, msg.as_string())
#         server.quit()
#         print("Email sent successfully")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

###SEND EMAIL example FASTAPI_MAIL
# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# conf = ConnectionConfig(
#     MAIL_USERNAME="your_email@example.com",
#     MAIL_PASSWORD="your_email_password",
#     MAIL_FROM="your_email@example.com",
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.example.com",
#     MAIL_TLS=True,
#     MAIL_SSL=False,
#     USE_CREDENTIALS=True
# )

# async def send_email(to_email: str, subject: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[to_email],  # List of recipients
#         body=body,
#         subtype="plain"
#     )

#     fm = FastMail(conf)
#     await fm.send_message(message)



