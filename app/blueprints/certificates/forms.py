"""Certificate forms with dynamic field support."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional

FIELD_SCHEMAS = {
    '比赛获奖证书': [
        {'name': 'competition_name', 'label': '比赛名称', 'type': 'string', 'required': True},
        {'name': 'award_level', 'label': '获奖等级', 'type': 'select', 'options': ['一等奖', '二等奖', '三等奖', '优秀奖'], 'required': True},
        {'name': 'award_date', 'label': '获奖日期', 'type': 'date', 'required': True},
        {'name': 'organizer', 'label': '主办单位', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': False},
    ],
    '荣誉证书': [
        {'name': 'honor_title', 'label': '荣誉名称', 'type': 'string', 'required': True},
        {'name': 'grant_date', 'label': '授予日期', 'type': 'date', 'required': True},
        {'name': 'grantor', 'label': '授予单位', 'type': 'string', 'required': True},
        {'name': 'reason', 'label': '获得原因', 'type': 'text', 'required': False},
    ],
    '资格证': [
        {'name': 'certificate_name', 'label': '证书名称', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'expiry_date', 'label': '有效期至', 'type': 'date', 'required': False},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
    '职业技能等级证书': [
        {'name': 'skill_name', 'label': '职业技能名称', 'type': 'string', 'required': True},
        {'name': 'skill_level', 'label': '等级', 'type': 'select', 'options': ['五级/初级工', '四级/中级工', '三级/高级工', '二级/技师', '一级/高级技师'], 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
}


class CertificateBaseForm(FlaskForm):
    """Base form with fixed certificate fields."""
    certificate_type_id = SelectField('证书类型 / Certificate Type', coerce=int, validators=[DataRequired(message='请选择证书类型')])
    title = StringField('证书标题 / Title', validators=[DataRequired(message='请输入证书标题')])
    file = FileField('证书文件 / Certificate File', validators=[
        FileRequired(message='请选择证书文件'),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif'], '只能是 PDF 或图片文件')
    ])
    submit = SubmitField('提交 / Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.certificate import CertificateType
        self.certificate_type_id.choices = [
            (ct.id, ct.name) for ct in CertificateType.query.order_by('name').all()
        ]


class CertificateEditForm(FlaskForm):
    """Form for editing existing certificate (file optional)."""
    certificate_type_id = SelectField('证书类型 / Certificate Type', coerce=int, validators=[DataRequired(message='请选择证书类型')])
    title = StringField('证书标题 / Title', validators=[DataRequired(message='请输入证书标题')])
    file = FileField('证书文件 / Certificate File', validators=[Optional()])
    submit = SubmitField('保存 / Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.certificate import CertificateType
        self.certificate_type_id.choices = [
            (ct.id, ct.name) for ct in CertificateType.query.order_by('name').all()
        ]
