from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, URL

from .constants import (
    MAX_LINK_LEN,
    MAX_SHORT_ID_LEN,
    MIN_LINK_LEN
)


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(message='Введённый адрес не '
                                'соответствует формату URL'),
                    Length(MIN_LINK_LEN, MAX_LINK_LEN)]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Optional(),
                    Length(
                        max=MAX_SHORT_ID_LEN,
                        message=f'Максимум {MAX_SHORT_ID_LEN} символов')]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы для загрузки',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
