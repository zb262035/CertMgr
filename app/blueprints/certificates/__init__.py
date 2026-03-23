"""Certificates blueprint - Stub for Phase 1 base.html compatibility.

功能实现见 Phase 2 / Functionality implemented in Phase 2.
"""
from flask import Blueprint, abort

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')


@certificates_bp.route('/')
def list():
    """List user's certificates."""
    abort(503)  # Phase 2 才实现


@certificates_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload new certificate."""
    abort(503)  # Phase 2 才实现


@certificates_bp.route('/<int:cert_id>')
def detail(cert_id):
    """View certificate detail."""
    abort(503)  # Phase 2 才实现


@certificates_bp.route('/<int:cert_id>/edit', methods=['GET', 'POST'])
def edit(cert_id):
    """Edit certificate."""
    abort(503)  # Phase 2 才实现


@certificates_bp.route('/<int:cert_id>/delete', methods=['POST'])
def delete(cert_id):
    """Delete certificate."""
    abort(503)  # Phase 2 才实现
