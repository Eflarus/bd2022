from flask import Blueprint

bp = Blueprint('revaluations', __name__)

from app.main.revaluations import routes