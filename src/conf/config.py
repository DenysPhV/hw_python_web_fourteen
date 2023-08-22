from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:password@127.0.0.1:5432/denis_fill_fa"
    secret_key: str = "secret key"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "qwerty"
    mail_from: str = "example@meta.ua"
    mail_port: int = 456
    mail_server: str = "smtp.meta.ua"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    origins: str = "origins"
    # cloudinary_name: str
    # cloudinary_api_key: str
    # cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


# class Config:
#     DATABASE_URL = "postgresql+psycopg2://postgres:58796@127.0.0.1:5432/denis_fill_fa"
#
#
# config = Config