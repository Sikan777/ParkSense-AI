from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.entity.models import Blacklist
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        The verify_password function takes a plain-text password and a hashed password as arguments.
        It then uses the pwd_context object to verify that the plain-text password matches the hashed
        password.

        :param self: Make the method a bound method, which means that it can be called on instances of the class
        :param plain_password: Store the password that is entered by the user
        :param hashed_password: Compare the password that is stored in the database to the one entered by a user
        :return: True if the password is correct and false otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as an argument and returns the hashed version of that password.
        The hash is generated using the pwd_context object's hash method, which uses bcrypt to generate a secure hash.

        :param self: Represent the instance of the class
        :param password: str: Pass the password to be hashed into the function
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.
            Args:
                data (dict): A dictionary containing the user's information.
                expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to 15 minutes if not specified.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A jwt token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user's data to the function
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
            The function takes in a refresh_token as an argument and returns the email of the user if successful.
            If unsuccessful, it raises an HTTPException with status code 401 (Unauthorized) and detail message 'Could not validate credentials'.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that is sent from the client
        :return: The email address of the user who sent the refresh token
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    @staticmethod
    async def add_token_to_blacklist(user_id: int, token: str, db: AsyncSession = Depends(get_db)):
        """
        The add_token_to_blacklist function add a token to the blacklist.

        :param user_id: User ID associated with the token.
        :type user_id: int
        :param token: Token to be blacklisted.
        :type token: str
        :param db: Async database session.
        """
        existing_token = select(Blacklist).filter_by(token=token)
        existing_token = await db.execute(existing_token)
        existing_token = existing_token.scalar_one_or_none()
        if not existing_token:
            new_blacklist_token = Blacklist(user_id=user_id, token=token)
            db.add(new_blacklist_token)
            await db.commit()

    @staticmethod
    async def is_token_blacklisted(token: str, db: AsyncSession = Depends(get_db)):
        """
        The is_token_blacklisted function check if a token is blacklisted.

        :param token: Token to be checked.
        :type token: str
        :param db: Async database session.
        :type db: AsyncSession
        :return: Blacklisted token record if found, None otherwise.
        :rtype: Blacklisted | None
        """
        stmt = select(Blacklist).filter_by(token=token)
        blacklisted_token = await db.execute(stmt)
        blacklisted_token = blacklisted_token.scalar_one_or_none()
        return blacklisted_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, or raises an exception otherwise.

        :param self: Allow the function to access the class variables
        :param token: str: Receive the token from the authorization header
        :param db: AsyncSession: Pass the database session to the function
        :return: The user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        if await self.is_token_blacklisted(token, db):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token is blacklisted. Please log in again.",
                                headers={"WWW-Authenticate": "Bearer"})

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        if user.ban:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account has been banned.")
        return user

    async def get_current_admin(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        user = await self.get_current_user(token, db)
        return user


auth_service = Auth()
