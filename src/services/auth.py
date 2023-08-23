import logging
from datetime import datetime, timedelta
from typing import Optional

import redis as redis
import pickle

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from src.conf.config import settings
from src.database.connector import get_db
from src.repository import users
from src.conf import messages


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
    redis_db = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def create_email_token(self, data: dict):
        """
            encode the email token

            :param data: data to generate the email token
            :type data: NoteModel
            :return: token for email
            :rtype: token
            """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
            decode token for email

            :param token: token to decode email
            :type token: str
            :return: email
            :rtype: str
            """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    def get_hash(self, password: str):
        """
            password hash

            :param password: password to hashstring
            :type password: str
            :return: hash
            :rtype: str
             """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, password_hash):
        """
            password hash

            :param plain_password: password
            :type plain_password: str
            :param password_hash: hashstring
            :type password_hash: str
            :return: verify result
            :rtype: bool
            """
        return self.pwd_context.verify(plain_password, password_hash)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
            get user by token

            :param token: token to get user
            :type token: token
            :param db: current session to db
            :type db: Session
            :return: user
            :rtype: bool
            """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload["scope"] == "access_token":
                email = payload["sub"]
                if not email:
                    raise credentials_exception
            else:
                raise credentials_exception

        except JWTError as e:
            logging.info(e)
            raise credentials_exception
        user = self.redis_db.get(f"user:{email}")
        if not user:
            user = await users.get_user_by_email(email, db)
            if not user:
                raise credentials_exception
            await self.redis_db.set(f"user:{email}", pickle.dumps(user))
            await self.redis_db.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
            encode access token

            :param data: data to be encoded
            :type data: dict
            :param expires_delta: second to life token
            :type expires_delta: float
            :return: token
            :rtype: token
             """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=[self.ALGORITHM])
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
           encode refresh token

           :param data: data to be encoded
           :type data: dict
           :param expires_delta: second to life token
           :type expires_delta: float
           :return: token
           :rtype: token
           """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=1)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=[self.ALGORITHM])
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
            decode refresh token

            :param refresh_token: token to decode email
            :type refresh_token: str
            :return: email address
            :rtype: str
            """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_SCOPE_TOKEN)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.CLOUD_NOT_VALIDATE)


auth_service = Auth()
