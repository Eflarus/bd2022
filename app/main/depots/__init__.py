from flask import Blueprint

bp = Blueprint('depots', __name__)

from app.main.depots import routes