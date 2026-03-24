"""Certificate business logic services."""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.certificate import Certificate
from app.services.file_storage_service import FileStorageService


class CertificateService:
    """Service for certificate CRUD operations."""

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in CertificateService.ALLOWED_EXTENSIONS

    @staticmethod
    def create_certificate(user_id, title, certificate_type_id, file, dynamic_fields):
        """Create a new certificate with file upload."""
        if not file or not CertificateService.allowed_file(file.filename):
            raise ValueError('Invalid file type')

        original_filename = secure_filename(file.filename)

        # Save file using FileStorageService
        file_result = FileStorageService.save_file(file)
        file_path = file_result['path']
        file_size = file_result['size']
        file_mime_type = file.content_type

        certificate = Certificate(
            user_id=user_id,
            title=title,
            certificate_type_id=certificate_type_id,
            file_path=file_path,
            original_filename=original_filename,
            file_size=file_size,
            file_mime_type=file_mime_type,
            fields=dynamic_fields
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate

    @staticmethod
    def update_certificate(certificate, title, certificate_type_id, file=None, dynamic_fields=None):
        """Update existing certificate."""
        certificate.title = title
        certificate.certificate_type_id = certificate_type_id

        if file and CertificateService.allowed_file(file.filename):
            FileStorageService.delete_file(certificate.file_path)
            file_result = FileStorageService.save_file(file)
            certificate.original_filename = secure_filename(file.filename)
            certificate.file_path = file_result['path']
            certificate.file_size = file_result['size']
            certificate.file_mime_type = file.content_type

        if dynamic_fields is not None:
            certificate.fields = dynamic_fields

        certificate.updated_at = datetime.utcnow()
        db.session.commit()
        return certificate

    @staticmethod
    def delete_certificate(certificate):
        """Delete certificate and its file."""
        FileStorageService.delete_file(certificate.file_path)
        db.session.delete(certificate)
        db.session.commit()
