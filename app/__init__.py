from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from .models import db, User, Friendship
from app.config import Config
import matplotlib

matplotlib.use('Agg')

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)

    # Load configurations
    app.config.from_object(config_class)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    app.config['UPLOAD_FOLDER'] = config_class.UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = config_class.ALLOWED_EXTENSIONS

    # Initialize Flask extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import routes within the application context
    with app.app_context():
        from . import routes

    return app