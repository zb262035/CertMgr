"""Admin routes for user management and system administration."""
import secrets
from flask import render_template, abort, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.decorators import admin_required

from app.blueprints.admin import admin_bp


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
        flash('无法修改自己的管理员状态 / Cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    action = '提升为管理员' if user.is_admin else '降级为普通用户'
    flash(f'用户 {user.email} 已{action} / User {user.email} has been {action}.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/toggle-disabled', methods=['POST'])
@login_required
@admin_required
def toggle_disabled(user_id):
    """Toggle disabled status for a user (admin only).

    Cannot disable yourself to prevent lockout.
    """
    if user_id == current_user.id:
        flash('无法禁用自己的账号 / Cannot disable your own account.', 'danger')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    user.is_disabled = not user.is_disabled
    db.session.commit()
    action = '已禁用' if user.is_disabled else '已启用'
    flash(f'用户 {user.email} {action} / User {user.email} {action}.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    """Reset password for a user (admin only).

    Generates a new random password and sends it to the user's email.
    For now, displays the new password in a flash message (in production,
    this should be sent via email).
    """
    if user_id == current_user.id:
        flash('无法重置自己的密码 / Cannot reset your own password.', 'danger')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    new_password = secrets.token_urlsafe(12)
    user.set_password(new_password)
    db.session.commit()
    flash(f'用户 {user.email} 的新密码是：{new_password} / New password for {user.email}: {new_password}', 'warning')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account (admin only).

    Cannot delete yourself to prevent lockout.
    """
    if user_id == current_user.id:
        flash('无法删除自己的账号 / Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)
    user_email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'用户 {user_email} 已删除 / User {user_email} has been deleted.', 'success')
    return redirect(url_for('admin.list_users'))