"""Permission decorators for access control.

This module provides decorators for enforcing access control:
- @admin_required: Only admin users can access
- @owner_required: Only the owner of a resource can access
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Decorator that requires the current user to be an admin.

    Usage:
        @admin_required
        def admin_only_route():
            ...

    Returns:
        403 Forbidden if user is not authenticated or not admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def owner_required(get_owner_id):
    """Decorator factory that requires the current user to own the resource.

    Args:
        get_owner_id: Function that takes the resource and returns owner_id

    Usage:
        @owner_required(lambda cert: cert.user_id)
        def edit_certificate(cert_id):
            ...

    Returns:
        403 Forbidden if user is not authenticated or not owner
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            # Store the callable for later evaluation in the view
            decorated_function._owner_check = get_owner_id
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_resource_permission(resource, owner_id):
    """Check if current user has permission to access a resource.

    Args:
        resource: The resource object (must have user_id or owner_id attribute)
        owner_id: The ID of the owner (or callable that takes resource)

    Returns:
        True if current user is admin or owner

    Raises:
        403 Forbidden if user does not have permission
    """
    if current_user.is_admin:
        return True

    # Handle callable owner_id (from @owner_required decorator)
    if callable(owner_id):
        owner_id = owner_id(resource)

    # Get owner ID from resource
    resource_owner_id = getattr(resource, 'user_id', None) or getattr(resource, 'owner_id', None)

    if resource_owner_id != current_user.id:
        abort(403)

    return True