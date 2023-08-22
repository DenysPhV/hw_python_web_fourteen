from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from src.database.models import Note, User
from src.schemas import NoteModel


async def create(body: NoteModel, db: AsyncSession):
    """
        Creates a new note for a specific user.

        :param body: The data for the note to create.
        :type body: NoteModel
        :param user: The user to create the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The newly created note.
        :rtype: Note
        """
    note = Note(**body.model_dump())
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_all(user: User, db: AsyncSession):
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    return notes


async def get_one(note_id, user: User, db: AsyncSession):
    """
        Show a single note with the specified ID for a specific user.

        :param note_id: The ID of the note to update.
        :type note_id: int
        :param body: The updated data for the note.
        :type body: NoteUpdate
        :param user: The user to update the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The updated note, or None if it does not exist.
        :rtype: Note | None
        """
    note = await db.query(Note).filter(and_(Note.user_id == user.id, Note.id == note_id)).first()
    return note


async def update(note_id, body: NoteModel, user: User, db: AsyncSession):
    """
        Updates a single note with the specified ID for a specific user.

        :param note_id: The ID of the note to update.
        :type note_id: int
        :param body: The updated data for the note.
        :type body: NoteUpdate
        :param user: The user to update the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The updated note, or None if it does not exist.
        :rtype: Note | None
        """
    note = await get_one(note_id, user, db)
    if note:
        note.text = body.text
        await db.commit()
    return note


async def delete(note_id, user: User, db: AsyncSession):
    """
        Removes a single note with the specified ID for a specific user.

        :param note_id: The ID of the note to remove.
        :type note_id: int
        :param user: The user to remove the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The removed note, or None if it does not exist.
        :rtype: Note | None
        """
    note = await get_one(note_id, user, db)
    if note:
        await db.delete(note)
        await db.commit()
    return note
