"""Statistics routes for certificate analytics."""
from flask import render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from app.blueprints.statistics import statistics_bp
from app.decorators import admin_required


@statistics_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Statistics dashboard page (admin only)."""
    return render_template('statistics/dashboard.html')


@statistics_bp.route('/api/chart/<chart_type>')
@login_required
@admin_required
def chart_data(chart_type):
    """Return JSON data for charts.

    Args:
        chart_type: 'by_type', 'monthly_trend', 'by_user', 'recent'
    """
    now = datetime.utcnow()

    if chart_type == 'by_type':
        # Bar chart: certificate count by type
        data = db.session.query(
            CertificateType.name,
            func.count(Certificate.id)
        ).join(Certificate).group_by(CertificateType.name).all()

        return jsonify({
            'labels': [row[0] for row in data],
            'values': [row[1] for row in data]
        })

    elif chart_type == 'monthly_trend':
        # Line chart: certificates per month (last 12 months)
        start_date = now - timedelta(days=365)

        # Build complete date range
        months = []
        current = start_date
        while current <= now:
            months.append((current.year, current.month))
            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        # Query actual data
        data = db.session.query(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at),
            func.count(Certificate.id)
        ).filter(
            Certificate.created_at >= start_date
        ).group_by(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at)
        ).order_by(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at)
        ).all()

        # Create lookup dict
        data_dict = {(int(row[0]), int(row[1])): row[2] for row in data}

        # Fill in missing months with 0
        labels = [f'{y}-{m:02d}' for y, m in months]
        values = [data_dict.get((y, m), 0) for y, m in months]

        return jsonify({'labels': labels, 'values': values})

    elif chart_type == 'by_user':
        # Pie chart: top 10 users by certificate count
        from app.models.user import User
        data = db.session.query(
            User.email,
            func.count(Certificate.id)
        ).join(Certificate).group_by(User.id, User.email).order_by(
            func.count(Certificate.id).desc()
        ).limit(10).all()

        return jsonify({
            'labels': [row[0] for row in data],
            'values': [row[1] for row in data]
        })

    elif chart_type == 'recent':
        # Recent certificates (last 10)
        certs = Certificate.query.order_by(Certificate.created_at.desc()).limit(10).all()

        return jsonify({
            'data': [
                {
                    'id': c.id,
                    'title': c.title,
                    'type': c.certificate_type.name if c.certificate_type else 'Unknown',
                    'user': c.owner.email if c.owner else 'Unknown',
                    'date': c.created_at.strftime('%Y-%m-%d') if c.created_at else ''
                }
                for c in certs
            ]
        })

    return jsonify({'error': 'Unknown chart type'}), 400


@statistics_bp.route('/api/summary')
@login_required
@admin_required
def summary():
    """Return summary statistics."""
    total = Certificate.query.count()
    by_type = db.session.query(
        CertificateType.name,
        func.count(Certificate.id)
    ).join(Certificate).group_by(CertificateType.name).all()

    return jsonify({
        'total': total,
        'by_type': [{'name': row[0], 'count': row[1]} for row in by_type],
        'recent_30_days': Certificate.query.filter(
            Certificate.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
    })
