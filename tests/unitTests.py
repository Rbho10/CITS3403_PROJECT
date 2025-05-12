import unittest
from app import create_app, db
from app.models import User
from app.config import TestingConfig

class UnitTest(unittest.TestCase):

    def setUp(self):
        # Create an isolated app instance with testing config
        self.app = create_app(TestingConfig)
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
        # Create a user and test successful login
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

        response = self.client.post(
            '/login',
            data={'username': 'login_user', 'password': 'test123'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Dashboard page should include 'Dashboard'
        self.assertIn(b'Dashboard', response.data)

    def test_login_fail(self):
        # Invalid credentials should re-render the login form
        response = self.client.post(
            '/login',
            data={'username': 'wronguser', 'password': 'wrongpass'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # We expect to see the login form again (e.g. its heading “Welcome Back”)
        self.assertIn(b'Welcome Back', response.data)

    def test_logout_route(self):
        # Log in and then log out, verifying we land back on the welcome page
        with self.client:
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

            # Log in
            self.client.post(
                '/login',
                data={'username': 'logout_user', 'password': 'logoutpass'},
                follow_redirects=True
            )

            # Log out
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # The welcome page’s hero text should be present
            self.assertIn(b'What will you', response.data)

    def test_protected_route_requires_login(self):
        # Accessing a login_required page without auth should redirect
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location', ''))

if __name__ == '__main__':
    unittest.main()
