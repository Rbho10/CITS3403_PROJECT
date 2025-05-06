import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for sessions, CSRF, flash messages, etc.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(basedir, 'user.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Flask‐session behavior
    SESSION_PERMANENT = False
