from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserModel
from src.database.models import User


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
        Get user by email

        :param email: user's email in db
        :type email: str
        :param db: current async session to db
        :type db: AsyncSession
        :return: User | None
        :rtype: User | None
        """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
        Create a new user

        :param body: all field for new user
        :type body: UserModel
        :param db: current async session to db
        :type db: AsyncSession
        :return: User | None
        :rtype: User | None
        """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
        Set confirmed field for user in db

        :param email: user's email in db
        :type email: str
        :param db: current async session to db
        :type db: AsyncSession
        :return: None if user is not confirmed
        :rtype: None
        """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
        Update token for user

        :param user: all field for new user
        :type user: UserModel
        :param token: old token
        :type token: str
        :param db: current async session to db
        :type db: AsyncSession
        :return: None
        :rtype: None
        """
    user.refresh_token = token
    await db.commit()


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
        Update user's avatar

        :param email: all field for new user
        :type email: UserModel
        :param url: url for avatar image
        :type url: str
        :param db: current async session to db
        :type db: AsyncSession
        :return: User | None
        :rtype: User | None
        """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user

