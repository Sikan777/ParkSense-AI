from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repositories_users
from src.schemas.user import UserModel, TokenModel, UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['Authentication'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserModel object, which is validated by pydantic.
        The password is hashed using Argon2 and stored as such.


    :param body: UserModel: Get the data from the request body
    :param db: AsyncSession: Get the database session
    :return: A new user
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make authenticated requests against protected endpoints.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get a database session
    :return: A dictionary with the access_token, refresh_token and token type
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if user.ban:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You were banned by an administrator")

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        It takes in a refresh token and returns a new access_token,
        refresh_token, and the type of bearer.

    :param credentials: HTTPAuthorizationCredentials: Get the credentials from the request header
    :param db: AsyncSession: Access the database
    :return: A new access token and a new refresh token
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The logout function is used to log out a user by adding their refresh token to the blacklist.

    :param user: The current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: A message indicating successful logout.
    :rtype: dict
    """
    await auth_service.add_token_to_blacklist(user.id, user.refresh_token, db)

    return {"message": "Logout successful."}
