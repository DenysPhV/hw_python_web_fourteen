from fastapi import APIRouter, Depends, status, HTTPException, Security, BackgroundTasks, Request
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import users as repository_user
from src.schemas import UserResponse, UserModel, TokenModel, RequestEmail
from src.database.connector import get_db
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_task: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)):
    """
        router to create new user

        :param body: incoming user model
        :type body: UserModel
        :param background_tasks: to perform the task of sending a email
        :type background_tasks: BackgroundTasks
        :param request: incoming
        :type request: Request
        :param db: current async session to db
        :type db: AsyncSession
        :return: new user
        :rtype: dict
        """
    old_user = await repository_user.get_user_by_email(body.email, db)
    if old_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_hash(body.password)

    new_user = await repository_user.create_user(body, db)
    background_task.add_task(send_email, body.email, new_user.name, str(request.base_url))
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
        router to login user and create/refresh token

        :param body: password form data
        :type body: OAuth2PasswordRequestForm
        :param db: current async session to db
        :type db: AsyncSession
        :return: token JWT
        :rtype: dict
        """
    user = await repository_user.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_user.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    """
        router to refresh token

        :param credentials: data with old token
        :type credentials: HTTPAuthorizationCredentials
        :param db: current async session to db
        :type db: AsyncSession
        :return: token JWT
        :rtype: dict
        """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_user.get_user_by_email(email, db)

    if user.refresh_token is not token:
        await repository_user.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_user.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
        router to confirm email

        :param token: user token
        :type token: str
        :param db: current async session to db
        :type db: AsyncSession
        :return: token JWT
        :rtype: dict
        """
    email = await auth_service.get_email_from_token(token)
    user = await repository_user.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_user.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
        router to send email for confirmation

        :param body: form to send email
        :type body: RequestEmail
        :param background_tasks: to perform the task of sending a email
        :type background_tasks: BackgroundTasks
        :param request: incoming request
        :type request: Request
        :param db: current async session to db
        :type db: AsyncSession
        :return: new user
        :rtype: dict
        """
    user = await repository_user.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
