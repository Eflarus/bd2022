from flask import Blueprint

bp = Blueprint('stuff', __name__)

from app.main.stuff import routes