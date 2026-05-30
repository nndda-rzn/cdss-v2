"""Flask extension singletons. Bound to the app in create_app()."""
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.db.base import Base

db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
migrate = Migrate()
