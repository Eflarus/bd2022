from flask import Blueprint

bp = Blueprint('stores', __name__)

from app.main.stores import routes