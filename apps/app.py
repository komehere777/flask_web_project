from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config


db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '정상 로그인 되었습니다.'


def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])
    csrf.init_app(app)
    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)

    def create_admin():
        from apps.crud.models import User

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                password="admin",
                is_Admin=True,
            )
            db.session.add(admin)
            db.session.commit()

    app.before_request(create_admin)

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix='/crud')

    from apps.auth import views as auth_views
    app.register_blueprint(auth_views.auth, url_prefix='/auth')
    
    from apps.main import views as main_views
    app.register_blueprint(main_views.main, url_prefix='/')

    return app
