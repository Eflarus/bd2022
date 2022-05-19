from flask import Blueprint

bp = Blueprint('stock', __name__)

from app.main.stock import routes