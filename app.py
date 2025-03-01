import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
app.secret_key = os.environ.get("SESSION_SECRET")
# Using SQLite with an absolute path in the instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcp.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Register blueprints
from api import api
from dashboard import dashboard

# Mount API at root level for better domain flexibility
app.register_blueprint(api)
# Keep dashboard under /dashboard path
app.register_blueprint(dashboard, url_prefix='/dashboard')

with app.app_context():
    import models
    db.create_all()