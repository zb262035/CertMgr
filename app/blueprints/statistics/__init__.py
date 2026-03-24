"""Statistics blueprint for certificate analytics."""
from flask import Blueprint

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

from app.blueprints.statistics import routes
