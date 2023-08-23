from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from src.database.models import Note, User
from src.schemas import NoteModel


async def create(body: NoteModel, db: AsyncSession):
    """
        Creates a new note for a specific user.

           :param body: all parameters for new note
           :type body: NoteModel
           :param user: current user - contact owner
           :type user: User
           :param db: current session to db
           :type db: Session
           :return: Note | None
           :rtype: Note | None
        """
    note = Note(**body.model_dump())
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_all(user: User, db: AsyncSession):
    """
       get notes from current user

       :param user: current user - contact owner
       :type user: User
       :param db: current session to db
       :type db: Session
       :return: Note
       :rtype: List
       """
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    return notes


async def get_one(note_id, user: User, db: AsyncSession):
    """
       get note by db id

       :param note_id: id to find
       :type note_id: int
       :param user: current user - contact owner
       :type user: User
       :param db: current session to db
       :type db: Session
       :return: Note | None
       :rtype: Note | None
       """
    note = await db.query(Note).filter(and_(Note.user_id == user.id, Note.id == note_id)).first()
    return note


async def update(note_id, body: NoteModel, user: User, db: AsyncSession):
    """
        Update note, find by db id

        :param note_id: id to find
        :type note_id: int
        :param body: all new parameters for note update
        :type body: NoteModel
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Note | None
        :rtype: Note | None
        """
    note = await get_one(note_id, user, db)
    if note:
        note.text = body.text
        await db.commit()
    return note


async def delete(note_id, user: User, db: AsyncSession):
    """
        delete note find note by db id

        :param note_id: id to find
        :type note_id: int
        :param user: current user - contact owner
        :type user: User
        :param db: current session to db
        :type db: Session
        :return: Note | None
        :rtype: Note | None
        """
    note = await get_one(note_id, user, db)
    if note:
        await db.delete(note)
        await db.commit()
    return note
