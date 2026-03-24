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

    # Column mapping (matches DataTables column index)
    columns = ['id', 'title', 'type', 'created_at']

    # Base query - non-admin sees only own certificates
    query = Certificate.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    # Total count before filtering (recordsTotal)
    records_total = query.count()

    # Global search across title, type, and holder name (CERT-07)
    if search_value:
        search_filter = or_(
            Certificate.title.ilike(f'%{search_value}%'),
            Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search_value}%')),
            Certificate.owner.has(User.name.ilike(f'%{search_value}%')),
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
    """Return all certificate types for filter dropdown."""
    types = CertificateType.query.order_by('name').all()
    return jsonify([
        {'id': t.id, 'name': t.name} for t in types
    ])
