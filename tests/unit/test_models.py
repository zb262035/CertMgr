"""Unit tests for models."""
import pytest
from app.extensions import db
from app.models.user import User
from app.models.certificate import Certificate, CertificateType


class TestUserModel:
    """Test User model."""

    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(email='new@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.email == 'new@example.com'
            assert user.is_admin is False

    def test_password_hashing(self, app):
        """Test password is hashed."""
        with app.app_context():
            user = User(email='hash@example.com')
            user.set_password('secret123')
            db.session.add(user)
            db.session.commit()

            assert user.password_hash != 'secret123'
            assert user.check_password('secret123') is True
            assert user.check_password('wrong') is False

    def test_admin_user(self, app):
        """Test admin user creation."""
        with app.app_context():
            admin = User(email='admin@test.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

            assert admin.is_admin is True


class TestCertificateModel:
    """Test Certificate model."""

    def test_create_certificate(self, app):
        """Test certificate creation."""
        with app.app_context():
            user = User(email='owner@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            # Use existing cert type (seeded by create_app)
            cert_type = CertificateType.query.filter_by(name='比赛获奖证书').first()
            assert cert_type is not None

            cert = Certificate(
                user_id=user.id,
                certificate_type_id=cert_type.id,
                title='Test Certificate',
                file_path='test/path.pdf',
                fields={'test': 'value'}
            )
            db.session.add(cert)
            db.session.commit()

            assert cert.id is not None
            assert cert.title == 'Test Certificate'
            assert cert.fields['test'] == 'value'

    def test_certificate_to_dict(self, app):
        """Test certificate serialization."""
        with app.app_context():
            user = User(email='dict@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            cert_type = CertificateType.query.filter_by(name='资格证').first()
            assert cert_type is not None

            cert = Certificate(
                user_id=user.id,
                certificate_type_id=cert_type.id,
                title='Dict Test',
                file_path='dict/path.pdf'
            )
            db.session.add(cert)
            db.session.commit()

            data = cert.to_dict()
            assert data['title'] == 'Dict Test'
            assert data['type'] == '资格证'
            assert 'created_at' in data


class TestCertificateTypeModel:
    """Test CertificateType model."""

    def test_certificate_types_seeded(self, app):
        """Test that certificate types are seeded."""
        with app.app_context():
            types = CertificateType.query.all()
            assert len(types) >= 4
            names = [t.name for t in types]
            assert '比赛获奖证书' in names
            assert '荣誉证书' in names
            assert '资格证' in names
            assert '职业技能等级证书' in names
