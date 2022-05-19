from flask import Blueprint

bp = Blueprint('invoices', __name__)

from app.main.invoices import routes