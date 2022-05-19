from flask import Blueprint

bp = Blueprint('returns', __name__)

from app.main.returns import routes