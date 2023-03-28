from flask import Blueprint

# API-Blueprint erstellen
api = Blueprint('api', __name__)

from . import views
