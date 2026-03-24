"""API tests for certificate routes."""
import pytest
import json
from app.extensions import db
from app.models.user import User
from app.models.certificate import Certificate, CertificateType


class TestAuthAPI:
    """Test authentication API."""

    def test_login_success(self, client, app):
        """Test successful login."""
        with app.app_context():
            user = User(email='login@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/auth/login', data={
            'email': 'login@test.com',
            'password': 'test123'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_login_wrong_password(self, client, app):
        """Test login with wrong password."""
        with app.app_context():
            user = User(email='wrong@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

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

    def test_list_certificates_authenticated(self, auth_client):
        """Test listing certificates with auth."""
        response = auth_client.get('/certificates/')
        assert response.status_code == 200

    def test_api_types(self, auth_client):
        """Test certificate types API."""
        response = auth_client.get('/certificates/api/types')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_api_data(self, auth_client):
        """Test certificates data API."""
        response = auth_client.get('/certificates/api/data')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'draw' in data
        assert 'recordsTotal' in data
        assert 'recordsFiltered' in data
        assert 'data' in data


class TestCertificateCRUD:
    """Test certificate CRUD operations."""

    def test_create_certificate(self, auth_client, app):
        """Test creating a certificate."""
        with app.app_context():
            cert_type = CertificateType.query.first()

        # Create certificate via form
        response = auth_client.post('/certificates/upload', data={
            'title': 'New Test Certificate',
            'certificate_type_id': cert_type.id,
            'dynamic_fields_json': '{}'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_view_certificate_detail(self, auth_client, app):
        """Test viewing certificate detail."""
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            cert_type = CertificateType.query.first()

            cert = Certificate(
                user_id=user.id,
                certificate_type_id=cert_type.id,
                title='Detail Test Certificate',
                file_path=''
            )
            db.session.add(cert)
            db.session.commit()

            cert_id = cert.id

        response = auth_client.get(f'/certificates/{cert_id}')
        assert response.status_code == 200
        assert b'Detail Test Certificate' in response.data

    def test_delete_certificate(self, auth_client, app):
        """Test deleting a certificate."""
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            cert_type = CertificateType.query.first()

            cert = Certificate(
                user_id=user.id,
                certificate_type_id=cert_type.id,
                title='Delete Test Certificate',
                file_path=''
            )
            db.session.add(cert)
            db.session.commit()

            cert_id = cert.id

        response = auth_client.post(f'/certificates/{cert_id}/delete', follow_redirects=True)
        assert response.status_code == 200


class TestAdminAPI:
    """Test admin API endpoints."""

    def test_admin_statistics_requires_admin(self, auth_client):
        """Test statistics requires admin."""
        response = auth_client.get('/admin/statistics')
        assert response.status_code in [302, 403]  # Redirect or forbidden

    def test_admin_statistics_as_admin(self, admin_client):
        """Test statistics as admin."""
        response = admin_client.get('/admin/statistics')
        assert response.status_code == 200
