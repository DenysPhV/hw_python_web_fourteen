from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException, Path

from src.database.models import User
from src.database.connector import get_db
from src.services.auth import auth_service as auth
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repository_contact

router = APIRouter(prefix='/contacts', tags=['contacts'])
finder = APIRouter(prefix='/contacts/find', tags=['find'])


@router.get("/", response_model=List[ContactResponse])
async def get_all(cur_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
        Returns a list of contacts with limits

        :param skip: skip number of contacts
        :type skip: int
        :param limit: part of the number of contacts
        :type limit: int
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact
        :rtype: Contact
        """
    contacts = await repository_contact.get_all(cur_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create(body: ContactModel, cur_user: User = Depends(auth.get_current_user),
                 db: AsyncSession = Depends(get_db)):
    """
        route to create new contact

        :param body: all need field to create
        :type body: ContactModel
        :param cur_user: current user - note owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact
        :rtype: Contact
        """
    contact = await repository_contact.find_by_email(body.email, cur_user, db)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='some email use in ' + contact.last_name)
    else:
        contact = await repository_contact.create(body, cur_user, db)
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_one(contact_id: int = Path(ge=1), cur_user: User = Depends(auth.get_current_user),
                  db: AsyncSession = Depends(get_db)):
    """
        route to get contact by id

        :param contact_id: id of contact to found
        :type contact_id: int
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact
        :rtype: Contact
        """
    contact = await repository_contact.get_one(contact_id, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update(body: ContactModel, contact_id: int = Path(ge=1), cur_user: User = Depends(auth.get_current_user),
                 db: AsyncSession = Depends(get_db)):
    """
        update contact by db id

        :param body: all need field to update
        :type body: contactModel
        :param contact_id: id to find
        :type contact_id: int
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Note | None
        :rtype: Note | None
        """
    contact = await repository_contact.update(contact_id, body, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(contact_id: int = Path(ge=1), cur_user: User = Depends(auth.get_current_user),
                 db: AsyncSession = Depends(get_db)):
    """
        route to delete contact by contact id

        :param contact_id: id of contact to found
        :type contact_id: int
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = await repository_contact.delete(contact_id, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@finder.get("name/{contact_name}", response_model=ContactResponse)
async def find_by_name(contact_name: str, cur_user: User = Depends(auth.get_current_user),
                       db: AsyncSession = Depends(get_db)):
    """
        route to get contact by contact name

        :param contact_name: name of contact to found
        :type contact_name: str
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = await repository_contact.find_by_name(contact_name, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@finder.get("lastname/{lastname}", response_model=ContactResponse)
async def find_by_name(lastname: str, cur_user: User = Depends(auth.get_current_user),
                       db: AsyncSession = Depends(get_db)):
    """
       route to get contact by lastname

       :param lastname: lastname of contact to found
       :type lastname: str
       :param cur_user: current user - contact owner
       :type cur_user: User
       :param db: current session to db
       :type db: Session
       :return: Contact | None
       :rtype: Contact | None
       """
    contact = await repository_contact.find_by_lastname(lastname, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@finder.get("email/{email}", response_model=ContactResponse)
async def find_by_name(email: str, cur_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
        route to get contact by email address

        :param email: email of contact to found
        :type email: str
        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = await repository_contact.find_by_email(email, cur_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@finder.get("birthday/", response_model=List[ContactResponse])
async def get_all(cur_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
        route to get contact with bithday in 7 days

        :param cur_user: current user - contact owner
        :type cur_user: User
        :param db: current session to db
        :type db: Session
        :return: Contact
        :rtype: List
        """
    contacts = await repository_contact.find_birthday7day(cur_user, db)
    return contacts
