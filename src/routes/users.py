from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.car import CarRepository
from src.schemas.car import NewCarResponse
from src.schemas.user import UserResponse, UserProfile, UserUpdate, UserTelegram
from src.services.auth import auth_service
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be used by the
        get_current_active_user function. It uses the auth service to retrieve
        information about the current user, and returns it as a User object.

    :param user: User: Get the current user from the auth_service
    :return: The current user, if the user is authenticated
    """
    return user


@router.get("/{username}", response_model=UserProfile)
async def get_user_profile(userid: int, token: str = Depends(auth_service.oauth2_scheme),
                           db: AsyncSession = Depends(get_db)):
    """
    The get_user_profile function returns a user profile based on the username provided.

    :param userid: str: Get the username from the path
    :param token: str: Get the access token from the request
    :param db: AsyncSession: Pass the database session to the function
    :return: A user profile with the number of photos
    """
    # Verify the token and get the current user
    current_user = await auth_service.get_current_user(token, db)

    user_profile = await repositories_users.get_user_by_userid(userid, db)

    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user_profile


@router.patch("/me", response_model=UserResponse)
async def update_profile(user_update: UserUpdate, user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """
    The update_profile function update the profile of the currently authenticated user.

    :param user_update: UserUpdate instance containing the updated user information.
    :type user_update: UserUpdate
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user information.
    :rtype: UserResponse
    """
    updated_user = await repositories_users.update_user(user.email, user_update, db)

    return updated_user


@router.post("/ban_user/{user_id}")
async def ban_user(user_id: int, token: str, db: AsyncSession = Depends(get_db)):
    """
    The ban_user function updates the 'ban' attribute in the database.

    username: Username of the user to be banned.
    username: str
    db: Asynchronous SQLAlchemy session (dependency injection).
    db: AsyncSession
    :return: True if the user is successfully banned, False otherwise.
    :rtype: bool
    """
    user = await repositories_users.get_user_by_userid(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.ban = True
    await db.commit()
    await auth_service.add_token_to_blacklist(user_id, token, db)
    return {"msg": "User has been banned"}


@router.get("/cars/{user_id}", response_model=list[NewCarResponse], status_code=status.HTTP_200_OK)
async def get_cars_by_user(user_id: int, db: AsyncSession = Depends(get_db),
                           user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of cars for the specified user.

    :param user_id: The ID of the user for whom to retrieve the cars.
    :type user_id: int
    :param db: Asynchronous database session (dependency injection).
    :type db: AsyncSession
    :param user: The currently authenticated user (dependency injection).
    :type user: User
    :raises HTTPException: If the user is not an admin and is trying to access data of another user, a 403 FORBIDDEN error is raised.
    :return: A list of cars belonging to the specified user.
    :rtype: list[NewCarResponse]
    """
    if user.role != Role.admin and user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    car_repository = CarRepository(db)
    cars = await car_repository.get_cars_by_user(user_id)
    return cars


@router.get("/cars/{plate}", response_model=NewCarResponse, status_code=status.HTTP_200_OK)
async def get_car_by_plate(plate: str, db: AsyncSession = Depends(get_db),
                           admin: User = Depends(auth_service.get_current_admin)):
    if admin.role != Role.admin:
        raise HTTPException(status_code=400, detail="Not authorized to access this resource")
    car_repository = CarRepository(db)
    car = await car_repository.get_car_by_plate(plate)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post("/bind_chat_id", status_code=status.HTTP_200_OK)
async def bind_chat_id(request: UserTelegram, db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(request.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.chat_id = request.chat_id
    await db.commit()
    return {"message": "Chat ID bound successfully"}
