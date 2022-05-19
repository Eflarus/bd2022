from flask import Blueprint

bp = Blueprint('goods', __name__)

from app.main.goods import routes