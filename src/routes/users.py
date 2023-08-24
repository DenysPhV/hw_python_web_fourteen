import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connector import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service as auth
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(cur_user: User = Depends(auth.get_current_user)):
    """
        route to current user

        :param cur_user: current user from database
        :type cur_user: User
        :return: current user from database
        :rtype: User
        """
    return cur_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), cur_user: User = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_db)):
    """
        route for upload file

        :param file: url of new avatar file
        :type file: str
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current async session to db
        :type db: AsyncSession
        :return: user | None
        :rtype: User | None
        """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{cur_user.name}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{cur_user.name}').build_url(width=250, height=250, crop='fill')
    user = await repository_users.update_avatar(cur_user.email, src_url, db)
    return user
