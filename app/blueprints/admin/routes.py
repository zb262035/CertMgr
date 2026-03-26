"""Admin routes for user management and system administration."""
import secrets
from flask import render_template, abort, jsonify, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.department import Department
from app.decorators import admin_required, school_admin_required

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
    # Get all departments for batch operations (school admin only sees in UI)
    departments = Department.query.filter_by(status='active').order_by(Department.name).all()
    return render_template('admin/users.html', users=users, departments=departments)


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


# ============== Batch Operations ==============

@admin_bp.route('/users/set-role/<int:user_id>/<role>', methods=['POST'])
@login_required
@admin_required
def set_user_role(user_id, role):
    """Set a user's role (admin only)."""
    if user_id == current_user.id:
        flash('无法修改自己的角色 / Cannot modify your own role.', 'danger')
        return redirect(url_for('admin.list_users'))

    user = User.query.get_or_404(user_id)

    # Validate role
    if role not in ['user', 'dept_admin']:
        flash('无效的角色 / Invalid role.', 'danger')
        return redirect(url_for('admin.list_users'))

    user.role = role
    db.session.commit()
    flash(f'用户 {user.email} 已设为 {role} / User {user.email} set to {role}.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/batch-set-role', methods=['POST'])
@login_required
@admin_required
def batch_set_role():
    """Batch set role for multiple users."""
    user_ids = request.form.get('user_ids', '')
    role = request.form.get('role', '')

    if not user_ids or not role:
        flash('参数错误 / Invalid parameters.', 'danger')
        return redirect(url_for('admin.list_users'))

    if role not in ['user', 'dept_admin']:
        flash('无效的角色 / Invalid role.', 'danger')
        return redirect(url_for('admin.list_users'))

    ids = [int(uid) for uid in user_ids.split(',') if uid]

    # Cannot affect current user
    if current_user.id in ids:
        ids.remove(current_user.id)
        flash('已跳过当前用户 / Current user skipped.', 'warning')

    if not ids:
        return redirect(url_for('admin.list_users'))

    count = User.query.filter(User.id.in_(ids)).update({User.role: role}, synchronize_session=False)
    db.session.commit()

    flash(f'已更新 {count} 个用户的角色 / {count} users updated.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/batch-reset-password', methods=['POST'])
@login_required
@admin_required
def batch_reset_password():
    """Batch reset password for multiple users."""
    user_ids = request.form.get('user_ids', '')

    if not user_ids:
        flash('参数错误 / Invalid parameters.', 'danger')
        return redirect(url_for('admin.list_users'))

    ids = [int(uid) for uid in user_ids.split(',') if uid]

    # Cannot affect current user
    if current_user.id in ids:
        ids.remove(current_user.id)
        flash('已跳过当前用户 / Current user skipped.', 'warning')

    if not ids:
        return redirect(url_for('admin.list_users'))

    # Generate new passwords
    users = User.query.filter(User.id.in_(ids)).all()
    passwords = []
    for user in users:
        new_password = secrets.token_urlsafe(8)
        user.set_password(new_password)
        passwords.append(f'{user.email}: {new_password}')

    db.session.commit()

    flash(f'已重置 {len(users)} 个用户的密码 / {len(users)} passwords reset. 新密码: {passwords[0] if passwords else "N/A"}', 'warning')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/batch-delete', methods=['POST'])
@login_required
@admin_required
def batch_delete():
    """Batch delete multiple users."""
    user_ids = request.form.get('user_ids', '')

    if not user_ids:
        flash('参数错误 / Invalid parameters.', 'danger')
        return redirect(url_for('admin.list_users'))

    ids = [int(uid) for uid in user_ids.split(',') if uid]

    # Cannot delete current user
    if current_user.id in ids:
        ids.remove(current_user.id)
        flash('已跳过当前用户 / Current user skipped.', 'warning')

    if not ids:
        return redirect(url_for('admin.list_users'))

    count = User.query.filter(User.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    flash(f'已删除 {count} 个用户 / {count} users deleted.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/batch-set-department', methods=['POST'])
@login_required
@school_admin_required
def batch_set_department():
    """Batch set department for multiple users (school admin only)."""
    user_ids = request.form.get('user_ids', '')
    department_id = request.form.get('department_id', type=int)

    if not user_ids:
        flash('参数错误 / Invalid parameters.', 'danger')
        return redirect(url_for('admin.list_users'))

    if not department_id:
        flash('请选择部门 / Please select a department.', 'danger')
        return redirect(url_for('admin.list_users'))

    # Verify department exists
    department = Department.query.get(department_id)
    if not department:
        flash('部门不存在 / Department not found.', 'danger')
        return redirect(url_for('admin.list_users'))

    ids = [int(uid) for uid in user_ids.split(',') if uid]

    # Cannot affect current user
    if current_user.id in ids:
        ids.remove(current_user.id)
        flash('已跳过当前用户 / Current user skipped.', 'warning')

    if not ids:
        return redirect(url_for('admin.list_users'))

    count = User.query.filter(User.id.in_(ids)).update(
        {User.department_id: department_id},
        synchronize_session=False
    )
    db.session.commit()

    flash(f'已将 {count} 个用户移到部门 {department.name} / {count} users moved to {department.name}.', 'success')
    return redirect(url_for('admin.list_users'))