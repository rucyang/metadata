# -*- coding:utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_admin import Admin
import flask_whooshalchemyplus as whooshalchemy
from flask_babelex import Babel
from flask_wtf.csrf import CSRFProtect


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
admin = Admin(name='后台管理', template_mode='bootstrap3')
db = SQLAlchemy()
babel = Babel()
csrf = CSRFProtect()

# 注册用认证
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    whooshalchemy.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)

    from .models import User, Role, File, UserView, \
        RoleView, FileView, TagView, Tag, Dossier, \
        DossierView

    admin.add_view(UserView(User, db.session, name='用户管理'))
    admin.add_view(RoleView(Role, db.session, name='权限管理'))
    admin.add_view(FileView(File, db.session, name='资源管理'))
    # admin.add_view(TagView(Tag, db.session, name='标签管理'))
    admin.add_view(DossierView(Dossier, db.session, name='案卷管理'))

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
