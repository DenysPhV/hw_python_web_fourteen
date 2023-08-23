from datetime import date, datetime
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import ContactModel
from src.database.models import Contact, User


async def create(body: ContactModel, db: AsyncSession):
    """
        Create a new contact

        :param body: all parameters for new contact
        :type body: ContactModel
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = Contact(**body.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_all(user: User, db: AsyncSession):
    """
        get part of contact from current user

        :param skip: number of contacts to skip
        :type skip: int
        :param limit: number of contacts to return
        :type limit: int
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: part of contact from current user
        :rtype: List
        """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    return contacts


async def get_one(contact_id, user: User, db: AsyncSession):
    """
        get contact by db id

        :param contact_id: id to find
        :type contact_id: int
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    return contact


async def update(contact_id, body: ContactModel, user: User, db: AsyncSession):
    """
        Update contact field, find by db id

        :param contact_id: id to find
        :type contact_id: int
        :param body: all new parameters for contact
        :type body: ContactModel
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = await get_one(contact_id, user, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.birthday = body.birthday
        await db.commit()
    return contact


async def delete(contact_id, user: User, db: AsyncSession):
    """
        delete contact find contact by db id

        :param contact_id: id to find
        :type contact_id: int
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = await get_one(contact_id, user, db)
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def find_by_name(contact_name, user: User, db: AsyncSession):
    """
        get contact by first name in db

        :param contact_name: name to find
        :type contact_name: str
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.first_name == contact_name)).first()
    return contact


async def find_by_lastname(lastname, user: User, db: AsyncSession):
    """
        get contact by last name in db

        :param lastname: lastname to find
        :type lastname: str
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Contact | None
        :rtype: Contact | None
        """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.last_name == lastname)).first()
    return contact


async def find_by_email(email, user: User, db: AsyncSession):
    """
          get contact by email in db

          :param email: name to find
          :type email: str
          :param user: current user - contact owner
          :type user: User
          :param db: current session to db
          :type db: Session
          :return: Contact | None
          :rtype: Contact | None
          """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.email == email)).first()
    return contact


async def find_birthday7day(user: User, db: AsyncSession):
    """
        contact with birthday next 7 days

        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: contact with birthday next 7 days
        :rtype: List
        """

    contacts = []
    db_contacts = await get_all(user, db)
    today = date.today()
    for db_contact in db_contacts:
        birthday = db_contact.birthday
        shift = (datetime(today.year, birthday.month, birthday.day).date() - today).days
        if shift < 0:
            shift = (datetime(today.year + 1, birthday.month, birthday.day).date() - today).days
        if shift <= 7:
            contacts.append(db_contact)
    return contacts
