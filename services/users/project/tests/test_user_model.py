import unittest
from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user
from sqlalchemy.exc import IntegrityError


class TestUserModel(BaseTestCase):

    def test_add_user(self):

        user = add_user(
            username='justatest',
            email='test@test.com',
            password='pass')

        self.assertTrue(user.id)
        self.assertEqual(user.username, 'justatest')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.active)
        self.assertTrue(user.password)

    def test_add_user_duplicate_username(self):
        add_user(username='justatest', email='test@test.com', password='pass')

        dupe_user = User(
            username='justatest',
            email='test2@test.com',
            password='pass')
        db.session.add(dupe_user)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_add_user_duplicate_email(self):
        add_user(
            username='justatest',
            email='test@test.com',
            password='pass')

        dupe_user = User(
            username='justatest2',
            email='test@test.com',
            password='pass')
        db.session.add(dupe_user)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_to_json(self):
        user = add_user(
            username='justatest',
            email='test@test.com',
            password='pass')

        self.assertTrue(isinstance(user.to_json(), dict))

    def test_passwords_are_random(self):

        user_one = add_user('justatest', 'test@test.com', 'greaterthaneight')
        user_two = add_user('justatest2', 'test2@test.com', 'greaterthaneight')

        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        user = add_user('test', 'test@test.com', 'pass')
        auth_token = user.encode_auth_token(user.id)

        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = add_user('test', 'test@test.com', 'pass')
        auth_token = user.encode_auth_token(user.id)

        self.assertEqual(user.id, User.decode_auth_token(auth_token))


if __name__ == '__main__':
    unittest.main()
