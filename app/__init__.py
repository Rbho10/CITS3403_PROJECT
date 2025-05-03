from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate

from .models import db, User
from app.config import Config
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
# ← load everything from your Config class
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# import your routes so ‘app’ and ‘db’ are in scope
from . import routes
