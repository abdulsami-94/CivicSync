from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.citizen import citizen as citizen_bp
    app.register_blueprint(citizen_bp)

    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.staff import staff as staff_bp
    app.register_blueprint(staff_bp, url_prefix='/staff')

    return app
