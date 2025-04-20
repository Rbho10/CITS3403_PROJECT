from flask import Flask, jsonify
from .models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db' #path to db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #false to save memory
app.config['SQLALCHEMY_ECHO'] = True #echo SQL queries to the console for debugging
app.config['SECRET_KEY'] = 'secret_key' # for storing a user login state, flash messages like alerts, for user login/logout, etc.

db.init_app(app) #initialize the database with the app

from . import routes


