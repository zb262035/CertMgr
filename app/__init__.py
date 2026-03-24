from flask import Flask
from app.extensions import db, login_manager, csrf


def create_app(config_name='dev'):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    if config_name == 'prod':
        app.config.from_object('app.config.ProdConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevConfig')
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Phase 2 stub - certificates blueprint (功能在 Phase 2 实现)
    from app.blueprints.certificates import certificates_bp
    app.register_blueprint(certificates_bp)

    # Import models to register them with SQLAlchemy
    from app.models import user

    # Create instance folder and upload directory
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create tables if needed (development only)
    with app.app_context():
        db.create_all()

        # Seed certificate types if they don't exist
        from app.models.certificate import CertificateType
        CERT_TYPES = [
            {'name': '比赛获奖证书', 'fields_schema': []},
            {'name': '荣誉证书', 'fields_schema': []},
            {'name': '资格证', 'fields_schema': []},
            {'name': '职业技能等级证书', 'fields_schema': []},
        ]
        for ct_data in CERT_TYPES:
            if not CertificateType.query.filter_by(name=ct_data['name']).first():
                ct = CertificateType(name=ct_data['name'], fields_schema=ct_data['fields_schema'])
                db.session.add(ct)
        db.session.commit()

    return app