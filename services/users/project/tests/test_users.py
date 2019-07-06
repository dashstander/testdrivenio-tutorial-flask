# services/users/project/tests/test_users.py

import json
import unittest

from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserService(BaseTestCase):
    """Tests for the Users Service"""

    def test_users(self):
        """Ensuring the /ping route behaves correctly."""
        response = self.client.get("/users/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'michael@mherman.org',
                    'password': 'pass'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('michael@mherman.org was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if payload json is incorrect."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown is payload json has incorrect keys."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'michael@mherman.org',
                                 'password': 'pass'}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):

        dupe_json = {'username': 'michael',
                     'email': 'michael@mherman.org',
                     'password': 'pass'}

        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dupe_json),
                content_type='application/json'
            )

            response = self.client.post(
                '/users',
                data=json.dumps(dupe_json),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure a single user can be queried correctly."""
        user = add_user(username='dash',
                        email='dstander@gmail.com',
                        password='pass')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('dash', data['data']['username'])
            self.assertIn('dstander@gmail.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """
        Ensure error is thrown if an id is not provided /
        is in incorrect format.
        """

        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        add_user('dash', 'dstander@gmail.com', 'pass')
        add_user('lily', 'lily@gmail.com', 'pass')

        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())

            status = data['status']
            users = data['data']['users']

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(users), 2)
            self.assertIn('dash', users[0]['username'])
            self.assertIn('dstander@gmail.com', users[0]['email'])
            self.assertIn('lily', users[1]['username'])
            self.assertIn('lily@gmail.com', users[1]['email'])
            self.assertIn('success', status)

    def test_main_with_no_users(self):
        """
        Ensure the main route behaves correctly when no users
        have been added to the database
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure the main route behaves correctly when there are users"""
        add_user('dash', 'dstander@zuora.com', 'pass')
        add_user('lily', 'lily@gmail.com', 'pass')

        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'dash', response.data)
            self.assertIn(b'lily', response.data)

    def test_main_add_user(self):
        """
        Ensure a new user can be added to the db via a POST request.
        """

        with self.client:
            response = self.client.post(
                '/',
                data={
                    'username': 'dash',
                    'email': 'dstander@gmail.com',
                    'password': 'pass'},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'dash', response.data)

    def test_add_user_invalid_json_key_no_password(self):
        """Ensure error is thrown if user doesn't have password."""

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'dash',
                    'email': 'dstander@gmail.com'
                }),
                content_type='application/json'
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])


if __name__ == '__main__':
    unittest.main()
