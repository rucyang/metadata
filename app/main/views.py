# -*- coding:utf-8 -*-
from flask import render_template, abort, \
    redirect, url_for, flash, current_app, request, \
    g
from flask_login import login_required, current_user
import os
from time import time

from . import main
from .. import db
from ..models import User, Role, File, Tag, Dossier
from .forms import EditProfileForm, EditProfileAdminForm, \
    FileMetaDataForm, EditFileMetaDataForm
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/scan')
def scan():
    page = request.args.get('page', 1, type=int)
    pagination = File.query.filter_by(verified=False).order_by(File.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['METADATA_FILES_PER_PAGE'],
        error_out=False
    )
    files = pagination.items
    return render_template('scan.html', files=files,
                           pagination=pagination)


@main.route('/me', methods=['GET', 'POST'])
@login_required
def me():
    pass


@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('您的个人资料已更新！')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('资料已更新！')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/upload-file', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = FileMetaDataForm()
    if form.validate_on_submit():

        filename = form.file_path.data.filename
        file_path = os.path.join(current_app.config['UPLOAD_DIR'], str(time())+filename)
        language = list(enumerate(current_app.config['LANGUAGES'], 1))[form.language.data-1][1]
        carrier_type = list(enumerate(current_app.config["FILE_TYPES"], 1))[form.carrier_type.data-1][1]
        classification_level = list(enumerate(current_app.config['CONFIDENTIALITIES'], 1))[form.classification_level.data-1][1]

        if form.relation_path.data.filename:
            relation = form.relation_path.data.filename
            relation_path = os.path.join(current_app.config['UPLOAD_DIR'], str(time())+relation)
        else:
            relation = None
            relation_path = None

        file = File(
            file_path=file_path,
            file_name=filename,
            creator=current_user,
            title_proper=form.title_proper.data,
            title_parallel=form.title_parallel.data,
            title_sub=form.title_sub.data,
            key_who=form.key_who.data,
            key_why=form.key_why.data,
            key_when=form.key_when.data,
            key_where=form.key_where.data,
            key_how=form.key_how.data,
            key_what=form.key_what.data,
            archive_num=form.archive_num.data,
            annotation=form.annotation.data,
            summary=form.summary.data,
            dossier=Dossier.query.get(form.dossier.data),
            language=language,
            relation_path=relation_path,
            relation_name=relation,
            archive_guide=form.archive_guide.data,
            dossier_guide=form.dossier_guide.data,
            coverage_note=form.coverage_note.data,
            classification_level = classification_level,
            retention_period=form.retention_period.data,
            creator_=form.creator_.data,
            publisher=form.publisher.data,
            contributor=form.contributor.data,
            rights=form.rights.data,
            date=form.date.data,
            version=form.version.data,
            record_type=form.record_type.data,
            carrier_type=carrier_type,
            number=form.number.data,
            specification=form.specification.data,
            identifier=form.identifier.data
        )

        db.session.add(file)
        db.session.commit()
        flash('文件上传成功！')
        form.file_path.data.save(file_path)
        if relation:
            form.relation_path.data.save(relation_path)
        return redirect(url_for('main.upload_file'))
    return render_template('upload_file.html', form=form)


@main.route('/delete-file/<int:ID>', methods=['GET'])
@login_required
def delete_file(ID):
    file = File.query.get_or_404(ID)
    file.verified = True
    db.session.add(file)
    db.session.commit()
    flash("删除成功！")
    return redirect(url_for('main.file_manage'))



@main.route('/edit-file/<int:ID>', methods=['GET', 'POST'])
@login_required
def edit_file(ID):
    file = File.query.get_or_404(ID)
    form = EditFileMetaDataForm()
    if form.validate_on_submit():
        file.title_proper = form.title_proper.data
        file.title_parallel = form.title_parallel.data
        file.title_sub = form.title_sub.data
        file.key_who = form.key_who.data
        file.key_why = form.key_why.data
        file.key_when = form.key_when.data
        file.key_where = form.key_where.data
        file.key_how = form.key_how.data
        file.key_what = form.key_what.data
        file.archive_num = form.archive_num.data
        file.annotation = form.annotation.data
        file.summary = form.summary.data
        file.dossier = Dossier.query.get(form.dossier.data)
        file.language = form.language.data
        file.archive_guide = form.archive_guide.data
        file.dossier_guide = form.dossier_guide.data
        file.coverage_note = form.coverage_note.data
        file.classification_level = form.classification_level.data
        file.retention_period = form.retention_period.data
        file.creator_ = form.creator_.data
        file.publisher = form.publisher.data
        file.contributor = form.contributor.data
        file.rights = form.rights.data
        file.date = form.date.data
        file.version = form.version.data
        file.record_type = form.record_type.data
        file.number = form.number.data
        file.specification = form.specification.data
        file.identifier = form.identifier.data
        db.session.add(file)
        db.session.commit()
        flash('档案资源已更新！')
        return redirect(url_for('main.file_manage'))

    form.file_name.data = file.file_name
    form.title_proper.data = file.title_proper
    form.title_parallel.data = file.title_parallel
    form.title_sub.data = file.title_sub
    form.key_who.data = file.key_who
    form.key_why.data = file.key_why
    form.key_when.data = file.key_when
    form.key_where.data = file.key_where
    form.key_how.data = file.key_how
    form.key_what.data = file.key_what
    form.archive_num.data = file.archive_num
    form.annotation.data = file.annotation
    form.summary.data = file.summary
    form.dossier.data = file.dossier
    form.language.data = file.language
    form.relation_name.data = file.relation_name
    form.archive_guide.data = file.archive_guide
    form.dossier_guide.data = file.dossier_guide
    form.coverage_note.data = file.coverage_note
    form.classification_level.data = file.classification_level
    form.retention_period.data = file.retention_period
    form.creator_.data = file.creator_
    form.publisher.data = file.publisher
    form.contributor.data = file.contributor
    form.rights.data = file.rights
    form.date.data = file.date
    form.version.data = file.version
    form.record_type.data = file.record_type
    form.number.data = file.number
    form.specification.data = file.specification
    form.identifier.data = file.identifier

    return render_template("edit_file.html", form=form, ID=ID)



@main.route('/search-result/', methods=['GET', 'POST'])
def search(key_word=None):
    searched_word = request.form['search']
    results = File.query.filter_by(verified=False).whoosh_search(searched_word,
                                       like=True, or_=True).all()
    return render_template('search_result.html', files=results)


@main.route('/file-profile/<int:id>', methods=["GET"])
def file_detail(id):
    file = File.query.get_or_404(id)
    return render_template('file_detail.html', file=file)

@main.route('/file-profile/<int:id>/er', methods=["GET"])
def er(id):
    file = File.query.get_or_404(id)
    return render_template('er.html', file=file)


@main.route('/file-manage')
@login_required
def file_manage():
    page = request.args.get('page', 1, type=int)
    pagination = File.query.filter_by(verified=False).filter_by(creator=current_user).order_by(File.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['METADATA_FILES_PER_PAGE'],
        error_out=False
    )
    files = pagination.items
    return render_template('file_manage.html', files=files, pagination=pagination)


@login_required
@main.route('/admin')
def admin_manage():
    return render_template('admin/index.html')


@main.route('/search-result/<field>-<keyword>')
def search_keyword(field, keyword):
    print(field)
    print(keyword)
    if field == '1':
        results = File.query.filter_by(key_who=keyword).all()
    elif field == '2':
        results = File.query.filter_by(key_why=keyword).all()
    elif field == '3':
        results = File.query.filter_by(key_when=keyword).all()
    elif field == '4':
        results = File.query.filter_by(key_where=keyword).all()
    elif field == '5':
        results = File.query.filter_by(key_how=keyword).all()
    else:
        results = File.query.filter_by(key_what=keyword).all()
    return render_template('search_result.html',
                           files=results)


@main.route('/add-dossier/', methods=['GET', 'POST'])
def add_dossier():
    new_dossier = request.form['dossier_name']
    if new_dossier == '':
        flash('案卷名不能为空！')
        return redirect(url_for('main.upload_file'))
    else:
        if Dossier.query.filter_by(name=new_dossier).first():
            flash('案卷已存在！')
            return redirect(url_for('main.upload_file'))
        dossier = Dossier(name=new_dossier)
        db.session.add(dossier)
        db.session.commit()
        flash('添加成功！')
        return redirect(url_for('main.upload_file'))


@main.route('/files/<file_type>', methods=['GET', 'POST'])
def scan_file(file_type):
    types = {'text': '文档', 'photo': '图片', 'vidio': '视频', 'audio': '音频', 'other': '其他'}
    classes = {'text': '', 'photo': '', 'vidio': '', 'audio': '', 'other': ''}
    g.carrier_type_id = file_type
    carrier_type = types.get(file_type)
    # if file_type is None:
    #     flash('请选择文件类型进行浏览！')
    #     return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = File.query.filter_by(verified=False).filter_by(carrier_type=carrier_type).order_by(File.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['METADATA_FILES_PER_PAGE'],
        error_out=False
    )
    if carrier_type in classes:
        classes[carrier_type] = 'active'
    files = pagination.items
    return render_template('file_list.html', files=files,
                           pagination=pagination, classes=classes, carrier_type=carrier_type)
