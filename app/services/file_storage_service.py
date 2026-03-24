"""File storage service with UUID-based naming and date sharding.

This module provides secure file storage for certificate files:
- UUID-based filenames prevent path traversal and filename collisions
- Date sharding (year/month) limits files per directory
- Original filename stored in metadata, not filesystem
- File type and size validation before saving
"""
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app


class FileStorageService:
    """Service for secure certificate file storage."""

    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed.

        Args:
            filename: Original filename

        Returns:
            True if extension is in ALLOWED_EXTENSIONS
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def get_upload_folder() -> Path:
        """Get the upload folder path from config.

        Returns:
            Path object for upload folder
        """
        folder = current_app.config.get('UPLOAD_FOLDER')
        if folder is None:
            folder = Path(current_app.instance_path) / 'uploads'
        elif isinstance(folder, str):
            folder = Path(folder)
        return folder

    @staticmethod
    def _secure_path(path: str) -> Path:
        """Validate path is within upload folder (prevent path traversal).

        Args:
            path: Relative path from upload folder

        Returns:
            Full path if valid

        Raises:
            ValueError: If path would escape upload folder
        """
        upload_folder = FileStorageService.get_upload_folder().resolve()
        full_path = (upload_folder / path).resolve()
        if not str(full_path).startswith(str(upload_folder)):
            raise ValueError("Invalid path: would escape upload folder")
        return full_path

    @staticmethod
    def validate_file(file) -> tuple[bool, str]:
        """Validate file before saving.

        Args:
            file: Werkzeug FileStorage object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file or file.filename == '':
            return False, "No file provided"

        if not FileStorageService.allowed_file(file.filename):
            return False, f"File type not allowed. Allowed: {', '.join(FileStorageService.ALLOWED_EXTENSIONS)}"

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > FileStorageService.MAX_FILE_SIZE:
            max_mb = FileStorageService.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"

        return True, ""

    @staticmethod
    def save_file(file) -> dict:
        """Save uploaded file with UUID name and date sharding.

        Args:
            file: Werkzeug FileStorage object

        Returns:
            Dict with keys: path, original_filename, size, stored_name

        Raises:
            ValueError: If file validation fails
        """
        is_valid, error = FileStorageService.validate_file(file)
        if not is_valid:
            raise ValueError(error)

        # Generate UUID-based filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        # Directory sharding by year/month
        now = datetime.now(timezone.utc)
        date_path = Path(str(now.year)) / f"{now.month:02d}"

        upload_folder = FileStorageService.get_upload_folder()
        full_dir = upload_folder / date_path
        full_dir.mkdir(parents=True, exist_ok=True)

        full_path = full_dir / unique_filename
        file.save(str(full_path))

        return {
            'path': str(date_path / unique_filename),
            'original_filename': secure_filename(file.filename),
            'size': os.path.getsize(full_path),
            'stored_name': unique_filename
        }

    @staticmethod
    def delete_file(path: str) -> bool:
        """Delete file from storage.

        Args:
            path: Relative path from upload folder (e.g., "2024/03/abc123.pdf")

        Returns:
            True if deleted, False if not found
        """
        try:
            full_path = FileStorageService._secure_path(path)
        except ValueError:
            return False

        if full_path.exists():
            full_path.unlink()
            return True
        return False

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists in storage.

        Args:
            path: Relative path from upload folder

        Returns:
            True if file exists
        """
        try:
            full_path = FileStorageService._secure_path(path)
        except ValueError:
            return False
        return full_path.exists()

    @staticmethod
    def get_file_size(path: str) -> int:
        """Get file size in bytes.

        Args:
            path: Relative path from upload folder

        Returns:
            File size in bytes, or 0 if not found
        """
        try:
            full_path = FileStorageService._secure_path(path)
        except ValueError:
            return 0
        if full_path.exists():
            return os.path.getsize(full_path)
        return 0