from flask import render_template, flash, redirect

from . import app

from .error_handlers import InvalidAPIUsage
from .forms import URLMapForm, FileUploadForm
from .models import URLMap
from .utils import get_or_create_url
from .yadisk import upload_all_files


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
