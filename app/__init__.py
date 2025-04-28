from flask import Flask, jsonify
from .models import db, User
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db' #path to db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #false to save memory
app.config['SQLALCHEMY_ECHO'] = True #echo SQL queries to the console for debugging
app.config['SECRET_KEY'] = 'secret_key' # for storing a user login state, flash messages like alerts, for user login/logout, etc.
app.config['SESSION_PERMANENT'] = False

db.init_app(app) #initialize the database with the app

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Name of your login route function

# Load user from session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import routes


