import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Create the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass
# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///scijournal_explorer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize SQLAlchemy with the app
db.init_app(app)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Import models after db initialization
from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Create database tables
with app.app_context():
    db.create_all()