"""API tests for certificate routes."""
import pytest
import json
from app.extensions import db
from app.models.user import User
from app.models.certificate import Certificate, CertificateType


def create_test_user(app, email='test@example.com', is_admin=False):
    """Create a test user in the database."""
    with app.app_context():
        user = User(email=email, is_admin=is_admin)
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        return user.id  # Return ID instead of object


def login(client, email, password='test123'):
    """Login a user."""
    client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


class TestAuthAPI:
    """Test authentication API."""

    def test_login_success(self, client, app):
        """Test successful login."""
        create_test_user(app, 'login@test.com')
        response = client.post('/auth/login', data={
            'email': 'login@test.com',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_wrong_password(self, client, app):
        """Test login with wrong password."""
        create_test_user(app, 'wrong@test.com')
        response = client.post('/auth/login', data={
            'email': 'wrong@test.com',
            'password': 'wrongpass'
        })
        assert response.status_code == 200  # Returns to login page


class TestCertificateAPI:
    """Test certificate API endpoints."""

    def test_list_certificates_unauthenticated(self, client):
        """Test listing certificates requires auth."""
        response = client.get('/certificates/')
        assert response.status_code == 302  # Redirect to login

    def test_list_certificates_authenticated(self, client, app):
        """Test listing certificates with auth."""
        create_test_user(app)
        login(client, 'test@example.com')
        response = client.get('/certificates/')
        assert response.status_code == 200

    def test_api_types(self, client, app):
        """Test certificate types API."""
        create_test_user(app)
        login(client, 'test@example.com')
        response = client.get('/certificates/api/types')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_api_data(self, client, app):
        """Test certificates data API."""
        create_test_user(app)
        login(client, 'test@example.com')
        response = client.get('/certificates/api/data')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'draw' in data
        assert 'recordsTotal' in data
        assert 'recordsFiltered' in data
        assert 'data' in data


class TestCertificateCRUD:
    """Test certificate CRUD operations."""

    def test_create_certificate(self, client, app):
        """Test creating a certificate."""
        create_test_user(app)
        login(client, 'test@example.com')

        with app.app_context():
            cert_type = CertificateType.query.filter_by(name='比赛获奖证书').first()
            cert_type_id = cert_type.id

        response = client.post('/certificates/upload', data={
            'title': 'New Test Certificate',
            'certificate_type_id': str(cert_type_id),
            'dynamic_fields_json': '{}'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_view_certificate_detail(self, client, app):
        """Test viewing certificate detail."""
        user_id = create_test_user(app)
        login(client, 'test@example.com')

        with app.app_context():
            cert_type = CertificateType.query.filter_by(name='资格证').first()
            cert = Certificate(
                user_id=user_id,
                certificate_type_id=cert_type.id,
                title='Detail Test Certificate',
                file_path=''
            )
            db.session.add(cert)
            db.session.commit()
            cert_id = cert.id

        response = client.get(f'/certificates/{cert_id}')
        assert response.status_code == 200

    def test_delete_certificate(self, client, app):
        """Test deleting a certificate."""
        user_id = create_test_user(app)
        login(client, 'test@example.com')

        with app.app_context():
            cert_type = CertificateType.query.filter_by(name='荣誉证书').first()
            cert = Certificate(
                user_id=user_id,
                certificate_type_id=cert_type.id,
                title='Delete Test Certificate',
                file_path=''
            )
            db.session.add(cert)
            db.session.commit()
            cert_id = cert.id

        response = client.post(f'/certificates/{cert_id}/delete', follow_redirects=True)
        assert response.status_code == 200


class TestAdminAPI:
    """Test admin API endpoints."""

    def test_admin_dashboard_requires_admin(self, client, app):
        """Test admin dashboard requires admin."""
        create_test_user(app)
        login(client, 'test@example.com')
        response = client.get('/admin/users')
        assert response.status_code in [302, 403]  # Redirect or forbidden

    def test_admin_dashboard_as_admin(self, client, app):
        """Test admin dashboard as admin."""
        create_test_user(app, 'admin@example.com', is_admin=True)
        login(client, 'admin@example.com')
        response = client.get('/admin/users')
        assert response.status_code == 200
