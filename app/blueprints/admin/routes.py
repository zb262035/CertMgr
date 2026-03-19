"""Admin routes for user management and system administration."""
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users in the system (admin only).

    Displays all registered users with their email, admin status,
    and registration date.
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user (admin only).

    Cannot toggle admin status on yourself to prevent lockout.
    """
    if user_id == current_user.id:
        abort(400, "Cannot modify your own admin status")

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return {'success': True, 'is_admin': user.is_admin}


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account (admin only).

    Cannot delete yourself to prevent lockout.
    """
    if user_id == current_user.id:
        abort(400, "Cannot delete your own account")

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {'success': True}