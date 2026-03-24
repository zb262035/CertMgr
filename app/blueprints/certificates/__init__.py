"""Certificates blueprint - Phase 2 implementation."""
from flask import Blueprint

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')

# Import routes and api modules to register them with the blueprint
# Order matters: both must be imported before the blueprint is registered
import app.blueprints.certificates.routes
import app.blueprints.certificates.api
