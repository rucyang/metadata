# -*- coding:utf-8 -*-
import os
# 获取当前文件所在目录，即metadata文件夹的路径
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """docstring for Config"""
    FILEPATH = os.path.join(basedir, 'testfile')
    UPLOAD_DIR = os.path.join(basedir, 'uploads')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    METADATA_MAIL_SUBJECT_PREFIX = '[档案资源知识服务系统]'
    METADATA_MAIL_SENDER = os.environ.get("METADATA_MAIL_SENDER")
    METADATA_ADMIN = os.environ.get('METADATA_ADMIN')
    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    CSRF_TOKEN = SECRET_KEY
    METADATA_FILES_PER_PAGE = 5
    FILE_TYPES = ['文档', '图片', '视频', '音频', '其他']
    LANGUAGES = ['中文', '英语', '日语', '法语', '西班牙语', '德语', '俄语', '其他']
    CONFIDENTIALITIES = ['无密级', '秘密', '机密', '绝密']

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    """docstring for DevConfig"""
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    # MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """docstring for ProductionConfig"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'dev': DevConfig,
    'test': TestConfig,
    'production': ProductionConfig,
    'default': DevConfig
}
