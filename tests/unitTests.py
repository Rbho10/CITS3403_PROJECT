import unittest
from app import create_app, db
from app.models import User
from app.config import TestingConfig

class UnitTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)  # create new isolated app instance
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        with self.app.app_context():
            user = User(
                username='tester',
                email='tester@example.com',
                first_name='Test',
                last_name='User'
            )
            user.set_password('securepass')
            db.session.add(user)
            db.session.commit()
            retrieved_user = User.query.filter_by(username='tester').first()
            self.assertIsNotNone(retrieved_user)

    def test_login_success(self):
        with self.app.app_context():
            user = User(
                username='login_user',
                email='login@example.com',
                first_name='Login',
                last_name='User'
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

        response = self.app.post('/login', data={
            'username': 'login_user',
            'password': 'test123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_login_fail(self):
        response = self.app.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_logout_route(self):
        with self.app:
            # First login
            with self.app.app_context():
                user = User(
                    username='logout_user',
                    email='logout@example.com',
                    first_name='Logout',
                    last_name='User'
                )
                user.set_password('logoutpass')
                db.session.add(user)
                db.session.commit()

            self.app.post('/login', data={
                'username': 'logout_user',
                'password': 'logoutpass'
            })

            response = self.app.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Logged out successfully', response.data)

    def test_protected_route_requires_login(self):
        response = self.app.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

if __name__ == '__main__':
    unittest.main()
