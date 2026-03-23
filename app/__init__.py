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

    return app