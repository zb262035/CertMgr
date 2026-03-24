"""Certificate models with JSONB dynamic fields."""
from datetime import datetime
from app.extensions import db


class CertificateType(db.Model):
    """Certificate type lookup table."""
    __tablename__ = 'certificate_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    fields_schema = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CertificateType {self.name}>'


class Certificate(db.Model):
    """Certificate record with dynamic fields stored in JSONB."""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    certificate_type_id = db.Column(db.Integer, db.ForeignKey('certificate_types.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_mime_type = db.Column(db.String(100))
    fields = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))
    certificate_type = db.relationship('CertificateType', backref=db.backref('certificates', lazy='dynamic'))

    def __repr__(self):
        return f'<Certificate {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.certificate_type.name if self.certificate_type else None,
            'type_id': self.certificate_type_id,
            'file_path': self.file_path,
            'file_mime_type': self.file_mime_type,
            'fields': self.fields or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
