import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import User, Contact
from src.schemas import ContactModel
from src.repository.contacts import (
    create,
    get_all,
    get_one,
    update,
    delete,
    find_by_name,
    find_by_email,
    find_by_lastname,
    find_birthday7day,
)
import datetime

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_create(self):
        body = ContactModel(
            first_name="test",
            last_name="last",
            email="test@email.com",
            phone="234-345-2343",
            birthday=datetime.datetime.now()
        )
        result = await create(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertIsNotNone(result.id)  # Check that id is not None

        print("Creating contact...")

    async def test_get_all(self):
        contacts = [Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_all(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_one_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_one(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_one_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_one(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_found(self):
        contact = Contact()
        body = ContactModel(
            first_name="test",
            last_name="last",
            email="test@email.com",
            phone="234-345-2343",
            birthday=datetime.datetime.now()
        )
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_not_found(self):
        body = ContactModel(
            first_name="test",
            last_name="last",
            email="test@email.com",
            phone="234-345-2343",
            birthday=datetime.datetime.now()
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    # ... (other test methods)

if __name__ == '__main__':
    unittest.main()
