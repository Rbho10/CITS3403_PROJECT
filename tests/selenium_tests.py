# tests/selenium_tests.py

import unittest
import time
from threading import Thread
from werkzeug.serving import make_server

from app import create_app
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
        # 1) Start Flask test server in background
        app = create_app(TestingConfig)
        app.testing = True
        cls.server = ServerThread(app)
        cls.server.start()
        time.sleep(1)  # let server spin up

        # 2) Launch headless Chrome
        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless")
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts
        )

        # 3) Sign up flow
        cls.driver.get("http://127.0.0.1:5000/signup")
        WebDriverWait(cls.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "first_name"))
        )
        cls.driver.find_element(By.NAME, "first_name").send_keys("Selenium")
        cls.driver.find_element(By.NAME, "last_name").send_keys("Test")
        cls.driver.find_element(By.NAME, "email").send_keys("seluser@example.com")
        cls.driver.find_element(By.NAME, "username").send_keys("selenium_user")
        cls.driver.find_element(By.NAME, "password").send_keys("selenium_pass")
        # instead of clicking a possibly-overlaid button, submit the form directly:
        cls.driver.find_element(By.TAG_NAME, "form").submit()
        WebDriverWait(cls.driver, 5).until(EC.url_contains("/login"))

        # 4) Log in once for all tests
        cls._login()

    @classmethod
    def _login(cls):
        d = cls.driver
        d.get("http://127.0.0.1:5000/login")
        WebDriverWait(d, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        d.find_element(By.NAME, "username").send_keys("selenium_user")
        d.find_element(By.NAME, "password").send_keys("selenium_pass")
        # again, submit the login form directly
        d.find_element(By.TAG_NAME, "form").submit()
        WebDriverWait(d, 5).until(EC.url_contains("/dashboard"))

    def test_01_signup_redirects_to_login(self):
        # after signup we should be on the login page
        self.assertIn("Login", self.driver.page_source)

    def test_02_login_shows_dashboard(self):
        # after login, we should see Dashboard
        self.assertIn("Dashboard", self.driver.page_source)

    def test_03_access_dashboard_directly(self):
        # revisit /dashboard with the same cookie/session
        self.driver.get("http://127.0.0.1:5000/dashboard")
        self.assertIn("Dashboard", self.driver.page_source)

    def test_04_logout_and_welcome(self):
        self.driver.get("http://127.0.0.1:5000/logout")
        WebDriverWait(self.driver, 5).until(EC.url_contains("/"))
        # welcome hero text
        self.assertIn("What will you", self.driver.page_source)

    def test_05_protected_redirects_to_login(self):
        # now logged out, accessing /dashboard should redirect to login
        self.driver.get("http://127.0.0.1:5000/dashboard")
        WebDriverWait(self.driver, 5).until(EC.url_contains("/login"))
        self.assertIn("Login", self.driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server.shutdown()
        cls.server.join()

if __name__ == "__main__":
    unittest.main()
