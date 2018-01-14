# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, \
    TextAreaField, SelectField, FileField, DateField
from wtforms.validators import Required, Length, Email
from wtforms import ValidationError
from flask import current_app

from ..models import Role, User, File, TagListField, Dossier


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('保存')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[Required(), Length(1, 64)])
    confirmed = BooleanField('是否确认账户')
    role = SelectField('用户角色', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('保存')

    def __init__(self, user, *args, **kw):
        super(EditProfileAdminForm, self).__init__(*args, **kw)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册！')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已注册！')


class FileMetaDataForm(FlaskForm):
    """docstring for FileMetaDatForm"""

    file_path = FileField('档案的导入', validators=[Required()])

    title_proper = StringField('正题名', validators=[Required()])
    title_parallel = StringField('并列题名：')
    title_sub = StringField('副题名及说明题名文字：')

    key_who = StringField('何人', validators=[Required()])
    key_why = StringField('何故：')
    key_when = StringField('何时', validators=[Required()])
    key_where = StringField('何地', validators=[Required()])
    key_how = StringField('何方式：')
    key_what = StringField('何事', validators=[Required()])

    archive_num = StringField('分类号', validators=[Required()])

    annotation = TextAreaField('附注：')
    summary = TextAreaField('提要：')

    dossier = SelectField('全宗或类：', coerce=int)

    language = SelectField('语言：', coerce=int)

    relation_path = FileField('相关资源：')

    archive_guide = StringField('档案馆指南：')
    dossier_guide = StringField('全宗指南：')
    coverage_note = StringField('卷、件内容覆盖范围说明：')

    classification_level = SelectField('密级：', coerce=int)
    retention_period = StringField('保管期限：')

    creator_ = StringField('责任者', validators=[Required()])
    publisher = StringField('发布者：')
    contributor = StringField('贡献者：')
    rights = StringField('权限：')

    date = StringField('时间', validators=[Required()])
    version = StringField('版本：')
    record_type = StringField('文种：')

    carrier_type = SelectField('载体类型：', coerce=int)
    number = StringField('数量及单位：')
    specification = StringField('规格：')

    record_num = StringField('文件编号：')
    identifier = StringField('档号', validators=[Required()])

    submit = SubmitField('上传')

    def __init__(self, *args, **kw):
        super(FileMetaDataForm, self).__init__(*args, **kw)
        self.carrier_type.choices = [
            (key, value)
            for key, value in enumerate(current_app.config['FILE_TYPES'], 1)
        ]
        self.language.choices = [
            (key, value)
            for key, value in enumerate(current_app.config['LANGUAGES'], 1)
        ]
        self.dossier.choices = [
            (dossier.id, dossier.name)
            for dossier in Dossier.query.order_by(Dossier.id).all()
        ]
        self.classification_level.choices = [
            (num, name)
            for num, name in enumerate(current_app.config['CONFIDENTIALITIES'], 1)
        ]

    def validate_title(self, field):
        if File.query.filter_by(title_proper=field.data).first():
            raise ValidationError('同名资源已上传！')

    def validate_tags(self, field):
        if field.data is None or field.data == '':
            raise ValidationError('该字段是必填字段')


class EditFileMetaDataForm(FlaskForm):
    """docstring for FileMetaDatForm"""

    file_name = StringField("档案资源名：")

    title_proper = StringField('正题名：')
    title_parallel = StringField('并列题名：')
    title_sub = StringField('副题名及说明题名文字：')

    key_who = StringField('何人：')
    key_why = StringField('何故：')
    key_when = StringField('何时：')
    key_where = StringField('何地：')
    key_how = StringField('何方式：')
    key_what = StringField('何事：')

    archive_num = StringField('分类号：', validators=[Required()])

    annotation = TextAreaField('附注：')
    summary = TextAreaField('提要：')

    dossier = SelectField('全宗或类：', coerce=int)

    language = SelectField('语言：', coerce=int)

    relation_name = StringField('相关资源名：')

    archive_guide = StringField('档案馆指南：')
    dossier_guide = StringField('全宗指南：')
    coverage_note = StringField('卷、件内容覆盖范围说明：')

    classification_level = SelectField('密级：', coerce=int)
    retention_period = StringField('保管期限：')

    creator_ = StringField('责任者：')
    publisher = StringField('发布者：')
    contributor = StringField('贡献者：')
    rights = StringField('权限：')

    date = StringField('时间：')
    version = StringField('版本：')
    record_type = StringField('文种：')

    carrier_type = SelectField('载体类型：', coerce=int)
    number = StringField('数量及单位：')
    specification = StringField('规格：')

    record_num = StringField('文件编号：')
    identifier = StringField('档号：')

    submit = SubmitField('保存')

    def __init__(self, *args, **kw):
        super(EditFileMetaDataForm, self).__init__(*args, **kw)
        self.carrier_type.choices = [
            (key, value)
            for key, value in enumerate(current_app.config['FILE_TYPES'], 1)
        ]
        self.language.choices = [
            (key, value)
            for key, value in enumerate(current_app.config['LANGUAGES'], 1)
        ]
        self.dossier.choices = [
            (dossier.id, dossier.name)
            for dossier in Dossier.query.order_by(Dossier.id).all()
        ]
        self.classification_level.choices = [
            (num, name)
            for num, name in enumerate(current_app.config['CONFIDENTIALITIES'], 1)
        ]
