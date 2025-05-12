import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class SeleniumTests(unittest.TestCase):
    """Emulate actual user interactions such as form submission, page navigation, and session handling.
    Validate the correctness of routes, login sessions, and redirection logic.
    """
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.driver.get("http://localhost:5000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_signup(self):
        driver = self.driver
        driver.get("http://localhost:5000/signup")
        driver.find_element(By.NAME, "username").send_keys("selenium_user")
        driver.find_element(By.NAME, "password").send_keys("selenium_pass")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)
        self.assertIn("Login", driver.page_source)

    def test_02_login(self):
        driver = self.driver
        driver.get("http://localhost:5000/login")
        driver.find_element(By.NAME, "username").send_keys("selenium_user")
        driver.find_element(By.NAME, "password").send_keys("selenium_pass")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)
        self.assertIn("Dashboard", driver.page_source)

    def test_03_access_dashboard(self):
        driver = self.driver
        driver.get("http://localhost:5000/dashboard")
        time.sleep(2)
        self.assertIn("Your Productivity Dashboard", driver.page_source)

    def test_04_logout(self):
        driver = self.driver
        driver.get("http://localhost:5000/logout")
        time.sleep(2)
        self.assertIn("Logged out successfully", driver.page_source)

    def test_05_protected_page_redirects(self):
        driver = self.driver
        driver.get("http://localhost:5000/dashboard")
        time.sleep(2)
        self.assertIn("Login", driver.page_source)

if __name__ == "__main__":
    unittest.main()
