"""Test configuration and fixtures."""
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.certificate import Certificate, CertificateType


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'

    with app.app_context():
        db.create_all()
        # Create test certificate type
        cert_type = CertificateType(name='比赛获奖证书')
        db.session.add(cert_type)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Create authenticated test client."""
    with app.app_context():
        # Create test user
        user = User(email='test@example.com')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()

    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'test123'
    }, follow_redirects=True)

    return client


@pytest.fixture
def admin_client(app, client):
    """Create admin test client."""
    with app.app_context():
        # Create admin user
        admin = User(email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=True)

    return client
