"""DataTables server-side API for certificate list."""
from flask import request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from app.models.user import User
from app.blueprints.certificates import certificates_bp


@certificates_bp.route('/api/data')
@login_required
def certificates_data():
    """DataTables server-side endpoint for certificate list with search and filter.

    Query parameters (DataTables standard):
    - draw: int, incremented on each request
    - start: int, offset for pagination
    - length: int, page size
    - search[value]: str, global search term
    - order[0][column]: int, column index for sorting
    - order[0][dir]: str, 'asc' or 'desc'

    Custom filter parameters:
    - filter_type: int, certificate_type_id
    - filter_date_from: str, date string (YYYY-MM-DD)
    - filter_date_to: str, date string (YYYY-MM-DD)
    - filter_department: int, department_id (school admin only)
    """
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')

    # Custom filters
    filter_type = request.args.get('filter_type', type=int)
    filter_date_from = request.args.get('filter_date_from')
    filter_date_to = request.args.get('filter_date_to')
    filter_department = request.args.get('filter_department', type=int)

    # Base query - non-admin sees only own certificates
    # Dept admin sees only their department's certificates
    query = Certificate.query
    if current_user.is_dept_admin():
        # Dept admin sees certificates from their department
        query = query.join(User, Certificate.user_id == User.id).filter(User.department_id == current_user.department_id)
    elif not current_user.is_school_admin():
        # Regular user sees only their own certificates
        query = query.filter_by(user_id=current_user.id)

    # Column mapping (matches DataTables column index)
    columns = ['id', 'title', 'type', 'created_at']

    # School admin can filter by department
    if filter_department and current_user.is_school_admin():
        query = query.join(User, Certificate.user_id == User.id).filter(User.department_id == filter_department)

    # Total count before filtering (recordsTotal)
    records_total = query.count()

    # Global search across title, type, and holder email
    if search_value:
        search_filter = or_(
            Certificate.title.ilike(f'%{search_value}%'),
            Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search_value}%')),
            Certificate.owner.has(User.email.ilike(f'%{search_value}%'))
        )
        query = query.filter(search_filter)

    # Apply custom filters
    if filter_type:
        query = query.filter(Certificate.certificate_type_id == filter_type)

    if filter_date_from:
        query = query.filter(Certificate.created_at >= filter_date_from)

    if filter_date_to:
        query = query.filter(Certificate.created_at <= filter_date_to)

    # Count after filtering (recordsFiltered)
    records_filtered = query.count()

    # Apply sorting and pagination
    order_col = columns[order_column] if order_column < len(columns) else 'created_at'
    order_func = getattr(Certificate, order_col).asc() if order_dir == 'asc' else getattr(Certificate, order_col).desc()
    query = query.order_by(order_func).offset(start).limit(length)

    records = query.all()

    return jsonify({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': [cert.to_dict() for cert in records]
    })


@certificates_bp.route('/api/types')
@login_required
def certificate_types():
    """Return all certificate types with schema for dynamic form rendering."""
    types = CertificateType.query.order_by('name').all()
    return jsonify([
        {
            'id': t.id,
            'name': t.name,
            'schema': t.get_schema()
        } for t in types
    ])


@certificates_bp.route('/api/types/<int:type_id>/schema')
@login_required
def certificate_type_schema(type_id):
    """Return schema for a specific certificate type."""
    ct = CertificateType.query.get_or_404(type_id)
    return jsonify({
        'id': ct.id,
        'name': ct.name,
        'schema': ct.get_schema()
    })


@certificates_bp.route('/api/user-fields')
@login_required
def user_fields():
    """Return all active user field definitions for dynamic form rendering."""
    from app.models.user_field import UserField
    fields = UserField.get_active_fields()
    return jsonify([f.to_dict() for f in fields])


@certificates_bp.route('/api/batch-delete', methods=['POST'])
@login_required
def batch_delete():
    """Batch delete certificates (admin only)."""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({'success': False, 'error': '无效请求 / Invalid request'}), 400

    ids = data.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'error': '未选择证书 / No certificates selected'}), 400

    # For dept admin, only allow deleting certificates from their department
    deleted_count = 0
    for cert_id in ids:
        cert = Certificate.query.get(cert_id)
        if cert:
            # Permission check
            if current_user.is_dept_admin():
                owner = User.query.get(cert.user_id)
                if owner and owner.department_id != current_user.department_id:
                    continue
            Certificate.query.filter_by(id=cert_id).delete()
            deleted_count += 1

    db.session.commit()
    return jsonify({'success': True, 'deleted': deleted_count})


@certificates_bp.route('/api/batch-update-status', methods=['POST'])
@login_required
def batch_update_status():
    """Batch update certificate status (admin only).

    Note: Requires 'status' field to be added to Certificate model.
    Currently returns not implemented.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    return jsonify({'success': False, 'error': '状态字段待添加 / Status field pending implementation'}), 501


# ============================================================
# Export API
# ============================================================

from datetime import datetime
from app.services.export_service import (
    generate_certificate_excel,
    get_available_fields,
    get_default_template,
    get_user_templates,
    DEFAULT_FIELDS
)
from app.models.export_template import ExportTemplate


@certificates_bp.route('/api/export')
@login_required
def export_certificates():
    """Export certificates to Excel file.

    Query parameters:
    - template_id: int (optional), use specified template
    - search: str (optional), search term
    - filter_type: int (optional), certificate type id
    - filter_department: int (optional), department id (admin only)
    - filter_date_from: str (optional), date string YYYY-MM-DD
    - filter_date_to: str (optional), date string YYYY-MM-DD
    """
    # Get template
    template_id = request.args.get('template_id', type=int)
    if template_id:
        template = ExportTemplate.query.get(template_id)
        if not template or template.created_by != current_user.id:
            template = get_default_template(current_user.id, current_user.is_school_admin())
    else:
        template = get_default_template(current_user.id, current_user.is_school_admin())

    fields = template.fields if template else DEFAULT_FIELDS

    # Build query with filters
    query = Certificate.query

    # Permission: regular user sees only own certificates
    if current_user.is_dept_admin():
        query = query.join(User, Certificate.user_id == User.id).filter(
            User.department_id == current_user.department_id
        )
    elif not current_user.is_school_admin():
        query = query.filter_by(user_id=current_user.id)

    # Apply filters
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                Certificate.title.ilike(f'%{search}%'),
                Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search}%')),
                Certificate.owner.has(User.email.ilike(f'%{search}%'))
            )
        )

    filter_type = request.args.get('filter_type', type=int)
    if filter_type:
        query = query.filter(Certificate.certificate_type_id == filter_type)

    filter_date_from = request.args.get('filter_date_from')
    if filter_date_from:
        query = query.filter(Certificate.created_at >= filter_date_from)

    filter_date_to = request.args.get('filter_date_to')
    if filter_date_to:
        query = query.filter(Certificate.created_at <= filter_date_to)

    # Department filter (admin only)
    filter_department = request.args.get('filter_department', type=int)
    if filter_department and current_user.is_school_admin():
        query = query.join(User, Certificate.user_id == User.id).filter(
            User.department_id == filter_department
        )

    certificates = query.all()

    # Generate Excel
    output = generate_certificate_excel(certificates, fields)

    # Generate filename with timestamp (ASCII-safe for HTTP headers)
    from urllib.parse import quote
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ascii_filename = f'certificates_{timestamp}.xlsx'
    chinese_filename = f'证书清单_{timestamp}.xlsx'

    response = output.getvalue()
    from flask import make_response
    resp = make_response(response)
    resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # Use ASCII filename as fallback, RFC 5987 compliant encoded Chinese filename
    resp.headers['Content-Disposition'] = f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{quote(chinese_filename)}"
    return resp


@certificates_bp.route('/api/export/templates')
@login_required
def export_templates_list():
    """Get user's export template list."""
    available_fields = get_available_fields()

    if current_user.is_school_admin():
        # Admin sees own templates
        templates = get_user_templates(current_user.id)
        if not templates:
            default = get_default_template(current_user.id, is_admin=True)
            templates = [default]
    else:
        # Non-admin: only global default template
        global_default = get_default_template(current_user.id, is_admin=False)
        templates = [global_default] if global_default else []

    return jsonify({
        'templates': [
            {
                'id': t.id,
                'name': t.name,
                'fields': t.fields,
                'is_default': t.is_default
            }
            for t in templates
        ],
        'available_fields': available_fields
    })


@certificates_bp.route('/api/export/templates', methods=['POST'])
@login_required
def export_templates_create():
    """Create a new export template (admin only)."""
    if not current_user.is_school_admin():
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '无效请求 / Invalid request'}), 400

    name = data.get('name', '').strip()
    fields = data.get('fields', [])
    is_default = data.get('is_default', False)

    if not name:
        return jsonify({'success': False, 'error': '模板名称不能为空 / Template name is required'}), 400

    if not fields or not isinstance(fields, list):
        return jsonify({'success': False, 'error': '请选择至少一个字段 / Please select at least one field'}), 400

    # If setting as default, unset other defaults
    if is_default:
        ExportTemplate.query.filter_by(created_by=current_user.id).update({'is_default': False})

    template = ExportTemplate(
        name=name,
        fields=fields,
        is_default=is_default,
        created_by=current_user.id
    )
    db.session.add(template)
    db.session.commit()

    return jsonify({
        'success': True,
        'template': {
            'id': template.id,
            'name': template.name,
            'fields': template.fields,
            'is_default': template.is_default
        }
    })


@certificates_bp.route('/api/export/templates/<int:template_id>', methods=['PUT'])
@login_required
def export_templates_update(template_id):
    """Update an export template (admin only)."""
    if not current_user.is_school_admin():
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    template = ExportTemplate.query.get_or_404(template_id)

    # Only allow updating own templates
    if template.created_by != current_user.id:
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '无效请求 / Invalid request'}), 400

    name = data.get('name', '').strip()
    fields = data.get('fields', [])
    is_default = data.get('is_default', False)

    if name:
        template.name = name

    if fields and isinstance(fields, list):
        template.fields = fields

    if is_default:
        ExportTemplate.query.filter(
            ExportTemplate.created_by == current_user.id,
            ExportTemplate.id != template_id
        ).update({'is_default': False})
        template.is_default = True

    db.session.commit()

    return jsonify({
        'success': True,
        'template': {
            'id': template.id,
            'name': template.name,
            'fields': template.fields,
            'is_default': template.is_default
        }
    })


@certificates_bp.route('/api/export/templates/<int:template_id>', methods=['DELETE'])
@login_required
def export_templates_delete(template_id):
    """Delete an export template (admin only)."""
    if not current_user.is_school_admin():
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    template = ExportTemplate.query.get_or_404(template_id)

    # Only allow deleting own templates
    if template.created_by != current_user.id:
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    # Cannot delete default template
    if template.is_default:
        return jsonify({'success': False, 'error': '不能删除默认模板 / Cannot delete default template'}), 400

    db.session.delete(template)
    db.session.commit()

    return jsonify({'success': True})


@certificates_bp.route('/api/export/templates/set-default/<int:template_id>', methods=['POST'])
@login_required
def export_templates_set_default(template_id):
    """Set a template as the default (admin only)."""
    if not current_user.is_school_admin():
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    template = ExportTemplate.query.get_or_404(template_id)

    if template.created_by != current_user.id:
        return jsonify({'success': False, 'error': '权限不足 / Insufficient permissions'}), 403

    # Unset all defaults for this user
    ExportTemplate.query.filter_by(created_by=current_user.id).update({'is_default': False})

    # Set this one as default
    template.is_default = True
    db.session.commit()

    return jsonify({'success': True})
