from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    email: str = Field(min_length=4, max_length=120)
    name: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=6, max_length=255)


class UserDb(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserModel):
    user: UserDb
    status: str = 'User added'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class ContactModel(BaseModel):
    first_name: str = Field(max_length=150, min_length=1)
    last_name: str = Field(max_length=150, min_length=1)
    email: EmailStr
    phone: str = Field(max_length=14, min_length=6,
                       pattern='\\d{3}\\-\\d{3}\\-\\d{2}\\-\\d{2}|'
                               '\\d{3}\\-\\d{3}\\-\\d{4}|'
                               '\\(\\d{3}\\)\\d{3}\\-\\d{2}\\-\\d{2}|'
                               '\\(\\d{3}\\)\\d{3}\\-\\d{4}|'
                               '\\(\\d{3}\\)\\d{7}|\\d{10}|'
                               '\\+\\d{12}$')
    birthday: datetime


class ContactResponse(ContactModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: datetime

    class Config:
        from_attributes = True


class NoteModel(BaseModel):
    text: str = Field(max_length=1000, min_length=1)
    contact_id: int = Field(1, gt=0)


class NoteResponse(NoteModel):
    id: int
    text: str
    contact: ContactResponse

    class Config:
        from_attributes = True


class RequestEmail(BaseModel):
    email: EmailStr
