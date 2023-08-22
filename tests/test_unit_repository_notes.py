import unittest

from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Note
from src.schemas import NoteModel
from src.repository.notes import (
    create,
    get_all,
    get_one,
    update,
    delete,
)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_all(self):
        notes = [Note(), ]
        self.session.query().filter().all.return_value = notes
        result = await get_all(user=self.user, db=self.session)
        self.assertEqual(result, notes)
        self.assertListEqual(result, notes)

    async def test_create(self):
        body = NoteModel(contact_id=1, text="test")
        result = await create(body=body, user=self.user, db=self.session)
        self.assertEqual(result.contact_id, body.contact_id)
        self.assertEqual(result.text, body.text)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_one_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_one(note_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_one_found(self):
        note = Note()
        self.session.query().filter().first.return_value = note
        result = await get_one(note_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_update_not_found(self):
        body = NoteModel(note_id=1, text="test")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update(note_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_found(self):
        note = Note()
        body = NoteModel(note_id=1, text="test")
        self.session.query().filter().first.return_value = note
        self.session.commit.return_value = None
        result = await update(note_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_delete_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete(note_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_delete_found(self):
        note = Note()
        self.session.query().filter().first.return_value = note
        result = await delete(note_id=1, user=self.user, db=self.session)
        self.assertEqual(result, note)


if __name__ == '__main__':
    unittest.main()