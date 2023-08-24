from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from src.conf.config import settings
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_SERVER=settings.mail_server,
    MAIL_PORT=settings.mail_port,
    MAIL_FROM_NAME='MY FAST API HW',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: str, username: str, host: str):
    """
        Sends an email

        :param email: email to send
        :type email: EmailStr
        :param username: username from db
        :type username: str
        :param host: host for email
        :type host: str
        :return: None
        :rtype: None
        """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")

    except ConnectionErrors as err:
        print(err)
