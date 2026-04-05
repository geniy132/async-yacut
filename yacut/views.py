import random
import re
import string

from flask import render_template, flash, redirect, url_for

from . import app, db
from .constants import (
    ALLOWED_CHARS,
    FORBIDDEN_IDS,
    MAX_SHORT_ID_LEN,
    RANDOM_ID_LEN,
    ERROR_INVALID_NAME,
    ERROR_ALREADY_EXISTS
)
from .error_handlers import InvalidAPIUsage
from .forms import URLMapForm, FileUploadForm
from .models import URLMap
from .yadisk import upload_all_files


def generate_short_id():
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(chars) for _ in range(RANDOM_ID_LEN))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def get_or_create_url(original, custom_id=None):
    if custom_id:
        is_invalid_format = not re.match(ALLOWED_CHARS, custom_id)
        is_too_long = len(custom_id) > MAX_SHORT_ID_LEN
        is_forbidden = custom_id in FORBIDDEN_IDS
        if is_invalid_format or is_too_long:
            raise InvalidAPIUsage(ERROR_INVALID_NAME)
        if URLMap.query.filter_by(short=custom_id).first() or is_forbidden:
            raise InvalidAPIUsage(ERROR_ALREADY_EXISTS)
        short_id = custom_id
    else:
        existing = URLMap.query.filter_by(original=original).first()
        if existing:
            return existing, False
        short_id = generate_short_id()
    url_map = URLMap(original=original, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return url_map, True


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        try:
            obj, created = get_or_create_url(
                form.original_link.data,
                form.custom_id.data
            )
            if not created:
                flash('Эта ссылка уже есть в базе')
            return render_template('urlmap.html', form=form, url=obj)
        except InvalidAPIUsage as e:
            flash(e.message)
    return render_template('urlmap.html', form=form)


@app.route('/<string:short>')
def redirect_to_url(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
async def add_file():
    form = FileUploadForm()
    if form.validate_on_submit():
        files_data = []
        for file in form.files.data:
            files_data.append((file.filename, file.read()))
        urls = await upload_all_files(files_data)
        for url in urls:
            flash(str(url))
        return render_template('add_file.html', form=form)
    return render_template('add_file.html', form=form)
