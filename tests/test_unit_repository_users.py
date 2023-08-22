import unittest

from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='test@example.com', db=self.session)
        self.assertIsNone(result)

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email='test@example.com', db=self.session)
        self.assertEqual(result, user)

    async def test_create_user_found(self):
        body = UserModel(name='test', email='test@example.com', password='12345678')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_confirmed_email_found(self):
        result = await confirmed_email(email='test@example.com', db=self.session)
        self.assertIsNone(result)

    async def test_update_token_found(self):
        result = await update_token(user=User(), token='123', db=self.session)
        self.assertIsNone(result)

    async def test_update_avatar_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await update_avatar(email='test@example.com', url='www.test.pic/1212.gif', db=self.session)
        self.assertEqual(result, user)


if __name__ == '__main__':
    unittest.main()
