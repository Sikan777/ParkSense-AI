import random
from typing import Optional
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.schemas.user import UserModel, UserUpdate
from src.services import auth
from src.static.telebot_tokens import tokens


async def create_user(body: UserModel, telegram_token: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the user data from the request body
    :param db: AsyncSession: Get the database session
    :return: A user object
    """

    is_first_user = await check_is_first_user(db)
    if is_first_user:
        new_user = User(**body.model_dump(), role=Role.admin)
    else:
        new_user = User(**body.model_dump(), telegram_token=telegram_token)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> User:
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
        If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A single user object
    """
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    user = user.unique().scalar_one_or_none()
    return user


async def get_user_by_userid(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_userid function takes a userid and returns the user object associated with that userid.
        If no such user exists, it returns None.

    :param user_id: str: Pass the username of the user to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object if the user_id exists in the database
    """
    stmt = select(User).filter_by(id=user_id)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    return user


async def check_is_first_user(db: AsyncSession):
    """
    The check_is_first_user function checks if the user is the first user in the database.
        If so, it returns True. Otherwise, it returns False.

    :param db: AsyncSession: Pass the database session to the function
    :return: True if the user table is empty, false otherwise
    """
    query = select(func.count()).select_from(User)
    result = await db.execute(query)
    return result.unique().scalar() == 0


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Specify the user that we want to update
    :param token: str | None: Update the refresh token of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    """
    user.refresh_token = token
    await db.commit()


async def update_user(email: str, user_update: UserUpdate, db: AsyncSession):
    """
    The update_user function updates the user information in the database.

    :param email: Email of the user to be updated.
    :type email: str
    :param user_update: UserUpdate instance containing updated user data.
    :type user_update: UserUpdate
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user instance or None if the user does not exist.
    :rtype: User or None
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()

    if user:
        for field, value in user_update.__dict__.items():
            if value is not None:
                if field == 'password':
                    setattr(user, field, auth.auth_service.get_password_hash(value))
                else:
                    setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
    else:
        return None


async def ban_user(username: str, db: AsyncSession):
    """
    The ban_user function updates the 'ban' attribute in the database.

    :param username: Username of the user to be banned.
    :type username: str
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: True if the user is successfully banned, False otherwise.
    :rtype: bool
    """
    stmt = select(User).filter_by(email=username)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    if user:
        user.ban = True
        await db.commit()
        return True
    else:
        return False
    
    
async def get_random_token(session: AsyncSession) -> str:
    available_tokens = list(tokens.values())
    
    while available_tokens:
        random_token = random.choice(available_tokens)
        # Check if the token is already assigned to a user
        result = await session.execute(select(User).filter(User.telegram_token == random_token))
        user = result.scalars().first()
        if not user:
            return random_token
        else:
            available_tokens.remove(random_token)

    raise ValueError("No available tokens found")
