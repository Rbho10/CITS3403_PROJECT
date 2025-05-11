import unittest

class UnitTest(unittest.TestCase):

    def test_successful_login():
        user = User(id=1, username="testuser")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        assertThat(try_to_login_user(1,"testuser","password"))