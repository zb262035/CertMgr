"""Test configuration and fixtures."""
import pytest
import sys
import os
import tempfile

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    # Use a temp file for SQLite to avoid connection issues
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    # Cleanup temp file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
