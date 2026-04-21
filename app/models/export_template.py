"""
ExportTemplate 模型 / Export Template Model

存储用户导出证书的模板配置
"""
from datetime import datetime
from app import db


class ExportTemplate(db.Model):
    """导出模板模型"""
    __tablename__ = 'export_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 模板名称，如"完整导出"
    fields = db.Column(db.JSON, nullable=False)  # ['title', 'owner_name', ...]
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认模板
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref='export_templates')

    def __repr__(self):
        return f'<ExportTemplate {self.name}>'

    @classmethod
    def get_default_for_user(cls, user_id):
        """获取用户的默认模板"""
        return cls.query.filter_by(created_by=user_id, is_default=True).first()

    @classmethod
    def get_global_default_template(cls):
        """获取全局默认模板（管理员设置的，所有用户共用）

        逻辑：找 created_by=1（管理员）的默认模板
        """
        return cls.query.filter_by(created_by=1, is_default=True).first()

    @classmethod
    def get_all_for_user(cls, user_id):
        """获取用户的所有模板"""
        return cls.query.filter_by(created_by=user_id).order_by(cls.is_default.desc(), cls.name).all()

    @classmethod
    def init_default_template(cls, user_id):
        """为用户初始化默认模板"""
        existing = cls.get_default_for_user(user_id)
        if existing:
            return existing

        default_fields = [
            'title',
            'owner_name',
            'department',
            'cert_type',
            'issue_date',
            'issuer',
            'created_at'
        ]

        template = cls(
            name='默认导出',
            fields=default_fields,
            is_default=True,
            created_by=user_id
        )
        db.session.add(template)
        db.session.commit()
        return template