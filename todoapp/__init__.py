from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Datenbank und Login-Manager initialisieren
db = SQLAlchemy()
login_manager = LoginManager()

from todoapp.routes import web

# App erstellen
def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MYSQL_DATABASE_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    login_manager.login_view = 'web.login'

    # Datenbank erstellen
    with app.app_context():
        db.create_all()

    # Blueprints registrieren
    app.register_blueprint(web)
    from todoapp.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app
