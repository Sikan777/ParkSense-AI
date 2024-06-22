import enum
from datetime import date
from typing import List

from sqlalchemy import String, func, DateTime, Enum, ForeignKey, Table, Integer, Float, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    user: str = "user"


user_car_association = Table(
    "user_car_association", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("car_id", Integer, ForeignKey("cars.id")),
)


class JoinTime:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        'created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)


class User(JoinTime, Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    parking_expenses_limit: Mapped[float] = mapped_column(Float, nullable=False, default=1000.0)  # Limits of parking expenses 
    telegram_token: Mapped[str] = mapped_column(String(150), unique=True, nullable=True)
    # telegram_token_id: Mapped[int] = mapped_column(Integer, ForeignKey("tokens.id"))
    # telegram_token: Mapped[str] = relationship("Token", back_populates="user")
    chat_id: Mapped[str] = mapped_column(String(150), unique=False, nullable=True)
    
    blacklist_tokens: Mapped["Blacklist"] = relationship(
        "Blacklist", back_populates="user", lazy="joined", uselist=True
    )
    cars: Mapped[List["Car"]] = relationship(
        secondary=user_car_association, back_populates="users", lazy="joined"
    )

# class Token(Base):
#     __tablename__ = "tokens"
    
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     token_value: Mapped[str] = mapped_column(String(150), unique=True, nullable=True)
    
#     # Связь с пользователем
#     user: Mapped[User] = relationship("User", back_populates="telegram_token")

class Blacklist(JoinTime, Base):
    __tablename__ = "blacklist"
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="blacklist_tokens",
                                        lazy="joined", cascade="all, delete")


class Image(JoinTime, Base):
    __tablename__ = "images"
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    current_plate: Mapped[str] = mapped_column(String(25), nullable=False, unique=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)

    history: Mapped["History"] = relationship(
        "History", back_populates="image", lazy="joined", cascade="all, delete"
    )


class Car(JoinTime, Base):
    __tablename__ = "cars"
    credit: Mapped[float] = mapped_column(Float, nullable=True)
    plate: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    model: Mapped[str] = mapped_column(String(128), nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)

    history: Mapped["History"] = relationship(
        "History", back_populates="car", lazy="joined", cascade="all, delete"
    )
    users: Mapped[List["User"]] = relationship(
        secondary=user_car_association, back_populates="cars", lazy="joined"
    )


class ParkingRate(JoinTime, Base):
    __tablename__ = "parking_rates"
    rate_per_hour: Mapped[float] = mapped_column(Float, default=5.0, nullable=True)
    rate_per_day: Mapped[float] = mapped_column(Float, default=50.0, nullable=True)
    number_of_spaces: Mapped[int] = mapped_column(Integer, default=50, nullable=True)
    history: Mapped["History"] = relationship("History", back_populates="rates",
                                              lazy="joined", cascade="all, delete", uselist=True)


class History(JoinTime, Base):
    __tablename__ = "history"
    entry_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    exit_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    parking_time: Mapped[float] = mapped_column(Float, nullable=True)
    cost: Mapped[float] = mapped_column(Float, nullable=True)
    paid: Mapped[bool] = mapped_column(default=False, nullable=True)
    number_free_spaces: Mapped[int] = mapped_column(Integer, nullable=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id"), nullable=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), nullable=True)
    rate_id: Mapped[int] = mapped_column(Integer, ForeignKey("parking_rates.id"), nullable=True)

    car: Mapped["Car"] = relationship("Car", back_populates="history", lazy="joined",
                                      cascade="all, delete")
    image: Mapped["Image"] = relationship("Image", back_populates="history", lazy="joined",
                                            cascade="all, delete")
    rates: Mapped["ParkingRate"] = relationship("ParkingRate", back_populates="history", lazy="joined",
                                                cascade="all, delete")
