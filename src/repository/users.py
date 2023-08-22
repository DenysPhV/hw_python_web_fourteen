from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserModel
from src.database.models import User


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    user.refresh_token = token
    await db.commit()


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user

