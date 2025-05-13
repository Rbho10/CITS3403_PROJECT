# tests/selenium_tests.py

import unittest
import time
from threading import Thread
from werkzeug.serving import make_server

from app import create_app, db
from app.models import User
from app.config import TestingConfig

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class ServerThread(Thread):
    def __init__(self, app):
        super().__init__()
        self.srv = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


class SeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1) start up our Flask app in testing mode
        app = create_app(TestingConfig)
        app.testing = True
        cls.server = ServerThread(app)
        cls.server.start()
        time.sleep(1)

        # 2) initialize the in-memory DB and insert our test user
        with app.app_context():
            db.create_all()
            u = User(
                first_name="Selenium",
                last_name="Test",
                email="seluser@example.com",
                username="selenium_user"
            )
            u.set_password("selenium_pass")
            db.session.add(u)
            db.session.commit()

        # 3) spin up headless Chrome
        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless")
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts
        )

        # 4) log in once for all tests
        cls._login()

    @classmethod
    def _login(cls):
        cls.driver.get("http://127.0.0.1:5000/login")
        WebDriverWait(cls.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        cls.driver.find_element(By.NAME, "username").send_keys("selenium_user")
        cls.driver.find_element(By.NAME, "password").send_keys("selenium_pass")
        # submit the form
        cls.driver.find_element(By.TAG_NAME, "form").submit()
        WebDriverWait(cls.driver, 5).until(
            EC.url_contains("/dashboard")
        )

    def test_00_signup_creates_account(self):
        # sign up a fresh user and verify redirection to login
        new_username = "new_user"
        driver = self.driver
        driver.get("http://127.0.0.1:5000/signup")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "first_name"))
        )
        driver.find_element(By.NAME, "first_name").send_keys("New")
        driver.find_element(By.NAME, "last_name").send_keys("User")
        driver.find_element(By.NAME, "email").send_keys("newuser@example.com")
        driver.find_element(By.NAME, "username").send_keys(new_username)
        driver.find_element(By.NAME, "password").send_keys("new_pass")
        driver.find_element(By.NAME, "confirm").send_keys("new_pass")
        driver.find_element(By.TAG_NAME, "form").submit()
        WebDriverWait(driver, 5).until(
            EC.url_contains("/login")
        )
        self.assertIn("Account created successfully", driver.page_source)
    def test_01_login_shows_dashboard(self):
        self.assertIn("Dashboard", self.driver.page_source)

    def test_02_access_dashboard_directly(self):
        # revisit /dashboard with the same session
        self.driver.get("http://127.0.0.1:5000/dashboard")
        self.assertIn("Dashboard", self.driver.page_source)

    def test_03_logout_and_welcome(self):
        self.driver.get("http://127.0.0.1:5000/logout")
        WebDriverWait(self.driver, 5).until(
            EC.url_contains("/")
        )
        self.assertIn("What will you", self.driver.page_source)

    def test_04_protected_redirects_to_login(self):
        # now that we're logged out, /dashboard should go to /login
        self.driver.get("http://127.0.0.1:5000/dashboard")
        WebDriverWait(self.driver, 5).until(
            EC.url_contains("/login")
        )
        self.assertIn("Login", self.driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server.shutdown()
        cls.server.join()


if __name__ == "__main__":
    unittest.main()
