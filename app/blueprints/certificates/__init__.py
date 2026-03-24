"""Certificates blueprint - Phase 2 implementation."""
from flask import Blueprint

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')

from app.blueprints.certificates import routes
