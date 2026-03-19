"""Pluggable authentication adapter interface.

This module defines the AuthAdapter abstract base class that enables
pluggable authentication backends. For Phase 1, only LocalAuthAdapter
(local database) is implemented. Phase 3 will add SSO adapters.
"""
from abc import ABC, abstractmethod
from flask import current_app


class AuthAdapter(ABC):
    """Abstract base class for authentication backends.

    All auth backends (local, OA, WeChat Work, CAS) must implement
    this interface so they can be swapped without changing application code.
    """

    @abstractmethod
    def authenticate(self, username: str, password: str):
        """Authenticate user with username and password.

        Args:
            username: User's email or username
            password: User's password

        Returns:
            User object if authentication successful, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        """Get user by ID.

        Args:
            user_id: User's integer ID

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        """Get user by email.

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        pass


class LocalAuthAdapter(AuthAdapter):
    """Local database authentication adapter.

    This adapter authenticates users against email/password stored
    in the local database using werkzeug.security password hashing.
    """

    def authenticate(self, username: str, password: str):
        """Authenticate against local database."""
        from app.models.user import User
        user = User.query.filter_by(email=username).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user_by_id(self, user_id: int):
        """Get user by ID from local database."""
        from app.models.user import User
        return User.query.get(int(user_id))

    def get_user_by_email(self, email: str):
        """Get user by email from local database."""
        from app.models.user import User
        return User.query.filter_by(email=email).first()


def get_auth_adapter():
    """Factory function to get the configured auth adapter.

    Returns the auth adapter based on AUTH_BACKEND config:
    - 'local' or unset: LocalAuthAdapter
    - 'sso': SSOAuthAdapter (Phase 3)
    """
    backend = current_app.config.get('AUTH_BACKEND', 'local')
    if backend == 'sso':
        from app.services.auth_backends import SSOAuthAdapter
        return SSOAuthAdapter()
    return LocalAuthAdapter()