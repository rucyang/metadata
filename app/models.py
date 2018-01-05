# -*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, redirect, url_for
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, AdminIndexView
from flask_login import current_user
from wtforms.widgets import TextInput
from wtforms import Field
import re
from jieba.analyse.analyzer import ChineseAnalyzer

from . import db
from . import login_manager


class Permission(object):
    UPLOAD_FILE = 0x01
    DOWNLOAD_FILE = 0x02
    REVIEW_UPLAOD_FILE = 0x04
    MANAGE_USER = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.UPLOAD_FILE | Permission.DOWNLOAD_FILE, True),
            'Moderator': (Permission.UPLOAD_FILE |
                          Permission.DOWNLOAD_FILE |
                          Permission.REVIEW_UPLAOD_FILE |
                          Permission.MANAGE_USER, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return self.name


class TagListField(Field):
    widget = TextInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(TagListField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.data:
            r = ''
            for obj in self.data:
                r += self.obj_to_str(obj)
            return ''
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            tags = self._remove_duplicates(
                [x.strip() for x in re.split(',|，', valuelist[0])]
            )
            self.data = [self.str_to_obj(tag) for tag in tags]
        else:
            self.data = None

    def pre_validate(self, form):
        pass

    @classmethod
    def _remove_duplicates(cls, seq):
        """去重"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item

    @classmethod
    def str_to_obj(cls, tag):
        """将字符串转换位obj对象"""
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj is None:
            tag_obj = Tag(name=tag)
        return tag_obj

    @classmethod
    def obj_to_str(cls, obj):
        """将对象转换为字符串"""
        if obj:
            return obj.name
        else:
            return u''


file_tag_ref = db.Table(
    'file_tag_ref',
    db.Column('file_id', db.Integer, db.ForeignKey('files.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)


class File(db.Model):
    """docstring for File"""
    __tablename__ = 'files'
    __searchable__ = ['title_proper', 'title_parallel', 'title_sub', 'key_who',
                      'key_why', 'key_when', 'key_what', 'key_where', 'key_how']
    __analyzer__ = ChineseAnalyzer()

    # 数据库存储基本字段
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    file_path = db.Column(db.String(128), unique=True)
    file_name = db.Column(db.String(128))
    verified = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 档案资源属性
    # 档案资源内容特征
    # 题名（Title）
    title_proper = db.Column(db.String(128), nullable=False)
    title_parallel = db.Column(db.String(128))
    title_sub = db.Column(db.String(128))

    # 主题词（Key Word）
    key_who = db.Column(db.String(128))
    key_why = db.Column(db.String(128))
    key_when = db.Column(db.String(128))
    key_where = db.Column(db.String(128))
    key_how = db.Column(db.String(128))
    key_what = db.Column(db.String(128))

    # 分类号（Classic Number）
    archive_num = db.Column(db.String(128))

    # 说明(Description)
    annotation = db.Column(db.String(1024))
    summary = db.Column(db.String(1024))

    # 出处(Source)
    # dossier = db.Column(db.String(128))  # 全宗或类
    dossier_id = db.Column(db.Integer, db.ForeignKey('dossiers.id'))

    # 语言（Language）
    language = db.Column(db.String(128))

    # 相关资源
    relation_path = db.Column(db.String(128), unique=True)
    relation_name = db.Column(db.String(128))

    # 范围（Coverage)
    archive_guide = db.Column(db.String(128))
    dossier_guide = db.Column(db.String(128))
    coverage_note = db.Column(db.String(1024))

    # 密级
    classification_level = db.Column(db.String(128))

    # 保管期限
    retention_period = db.Column(db.String(128))


    # 档案资源产权特征
    creator_ = db.Column(db.String(128))  # 责任者
    publisher = db.Column(db.String(128))  # 发布者
    contributor = db.Column(db.String(128))  # 其他责任者
    rights = db.Column(db.String(128))  # 权限

    # 档案资源形式特征
    # 时间
    date = db.Column(db.String(128))

    # 类型
    version = db.Column(db.String(128))
    record_type = db.Column(db.String(128))

    # 格式
    carrier_type = db.Column(db.String(128))
    number = db.Column(db.String(128))
    specification = db.Column(db.String(128))

    # 档号
    identifier = db.Column(db.String(128))

    # id = db.Column(db.Integer, primary_key=True)
    # timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    # tags = db.relationship('Tag', secondary=file_tag_ref,
    #                        backref=db.backref('files'))
    # file_path = db.Column(db.String(128), unique=True, index=True)
    # verified = db.Column(db.Boolean, default=False)
    #
    # title = db.Column(db.String(64), unique=True, index=True, nullable=False)
    # archive_num = db.Column(db.String(64))
    # confidentiality = db.Column(db.String(64))
    # department = db.Column(db.String(128))
    # dossier_id = db.Column(db.Integer, db.ForeignKey('dossiers.id'))
    # creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # subject = db.Column(db.String(64), index=True, nullable=False)
    # description = db.Column(db.Text, nullable=True)
    # publishers = db.Column(db.String(64), nullable=True)
    # contributors = db.Column(db.String(64), nullable=True)
    # date = db.Column(db.Date())
    # file_type = db.Column(db.String(64))
    # identifier = db.Column(db.String(64))
    # language = db.Column(db.String(64))
    # format = db.Column(db.String(64))
    # source = db.Column(db.Text())
    # location = db.Column(db.String(64))
    # rights = db.Column(db.String(64))

    def __repr__(self):
        return self.title_proper


class Dossier(db.Model):
    """docstring for Dodb.Model"""
    __tablename__ = 'dossiers'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    files = db.relationship('File', backref='dossier', lazy='dynamic')

    def __repr__(self):
        return self.name


class Tag(db.Model):
    """docstring fodb.Model"""
    __tablename__ = 'tags'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return self.name


class User(UserMixin, db.Model):
    """docstring for User"""
    __tablename__ = 'users'
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    files = db.relationship('File', backref='creator', lazy='dynamic')

    def __repr__(self):
        return self.username

    @property
    def password(self):
        raise AttributeError('密码不是可读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email

    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.role is None:
            if self.email == current_app.config['METADATA_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# 将AnonymousUser设置为用户未登录时的current_user的值
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AdminModelView(ModelView):

    """docstring for AdminModelView"""

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_administrator():
            return True
        return False

    # def inaccessible_callback(self, name, **kw):
    #     return redirect(url_for('main.user', next=request.url))


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return super(MyAdminIndexView, self).index()


class UserView(AdminModelView):
    """docstring for ClassName"""
    can_delete = True
    can_edit = True
    can_create = False

    column_labels = dict(
        username="用户名",
        email='邮箱',
        name='真实姓名',
        location='住址',
        role='用户角色',
        password_hash='密码哈希值',
        confirmed='是否确认账户',
        about_me='用户简介',
        member_since='注册时间',
        last_seen='上次登陆',
        files='上传文件'
    )

    column_exclude_list = (
        'password_hash',
        'about_me',
        'member_since',
        'last_seen',
        'confirmed'
    )


class RoleView(AdminModelView):
    """docstring for ClassName"""
    can_delete = True
    can_edit = True
    can_create = False

    column_labels = dict(
        name='角色名',
        permissions='权限',
        users='拥有用户',
        default='是否默认权限'
    )

    column_exclude_list = (
        'default',
    )


class FileView(AdminModelView):
    """docstring for ClassName"""
    can_delete = True
    can_edit = True
    can_create = False
    # form_overrides = dict(tags=TagListField)
    # column_display_pk = True
    column_display_all_relations = True
    column_searchable_list = (
        File.title_sub,
        File.title_parallel,
        File.title_proper,
        File.language,
        File.key_what,
        File.key_how,
        File.key_where,
        File.key_when,
        File.key_why,
        File.key_who
    )

    column_list = [
        "title_proper",
        "key_who",
        "archive_num",
        "annotation",
        "dossier",
        "language",
        "relation_name",
        "classification_level",
        "retention_period",
        "creator_",
        "publisher",
        "contributor",
        "rights",
        "date",
        "carrier_type",
        "identifier"
    ]

    column_labels = dict(
        id="索引编号",
        timestamp="上传时间",
        file_path="资源路径",
        file_name="档案资源名",
        verified="是否通过审核",
        creator_id="上传者ID",
        creator="上传者",
        title_proper="正题名",
        title_parallel="并列题名",
        title_sub="副题名及说明题名文字",
        key_who="何人",
        key_why="何故",
        key_when="何时",
        key_where="何地",
        key_how="何方式",
        key_what="何事",
        archive_num="分类号",
        annotation="附注",
        summary="提要",
        dossier_id="全宗或类ID",
        dossier="全宗或类",
        language="语言",
        relation_path="相关资源路径",
        relation_name="相关资源名",
        archive_guide="档案馆指南",
        dossier_guide="全宗指南",
        coverage_note="卷、件内容覆盖范围说明",
        classification_level="密级",
        retention_period="保管期限",
        creator_="责任者",
        publisher="发布者",
        contributor="贡献者",
        rights="权限",
        date="时间",
        version="版本",
        record_type="文种",
        carrier_type="载体类型",
        number="数量及单位",
        specification="规格",
        identifier="档号"
    )
    # inline_models = (Tag,)
    # column_labels = dict(
    #     tags='标签',
    #     timestamp='上传时间',
    #     file_path='保存路径',
    #     verified='是否通过审核',
    #     title='题名',
    #     subject='主题',
    #     description='描述',
    #     publishers='出版者',
    #     contributors='贡献者',
    #     date='存档日期',
    #     identifier='标识符',
    #     format='格式',
    #     source='档案来源',
    #     location='地理位置',
    #     rights='使用权限',
    #     creator='创建者',
    #     file_type='载体类型',
    #     language='语言',
    #     archive_num='档案文号',
    #     confidentiality='密级',
    #     department='存档单位'
    # )

    # column_list = (
    #     'title',
    #     'subject',
    #     'tags',
    #     'language',
    #     'archive_num',
    #     'confidentiality',
    #     'department',
    #     'publishers',
    #     'contributors',
    #     'source',
    #     'file_type',
    #     'date'
    # )

    # column_exclude_list = (
    #     'timestamp',
    #     'file_path',
    #     'identifier'
    #     )


class TagView(AdminModelView):
    """docstring for ClassName"""
    can_delete = True
    can_edit = True
    can_create = False
    column_labels = dict(
        name='标签名',
        files='包含该标签的档案资源'
    )


class DossierView(AdminModelView):
    """docstring for DossierView"""
    column_labels = dict(
        name='案卷名',
        files='该案卷下的档案资源'
    )
