from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.car import CarRepository
from src.schemas.car import NewCarResponse
from src.schemas.user import UserResponse, UserProfile, UserUpdate
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
async def get_user_profile(userid: int, db: AsyncSession = Depends(get_db)):
    """
    The get_user_profile function returns a user profile based on the username provided.

    :param userid: str: Get the username from the path
    :param db: AsyncSession: Pass the database session to the function
    :return: A user profile with the number of photos
    """
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


@router.patch("/admin/{username}/ban")
async def ban_user(username: str, current_user: User = Depends(auth_service.get_current_user),
                   db: AsyncSession = Depends(get_db)):
    """
    The ban_user function ban a user by the admin.

    :param username: Username of the user to be banned.
    :type username: str
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :raises HTTPException: If the current user is not an admin or if the user to be banned is not found.
    :return: A message indicating the success of the operation.
    :rtype: dict
    """
    if not current_user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    banned = await repositories_users.ban_user(username, db)
    if not banned:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"message": f"{username} has been banned."}


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
