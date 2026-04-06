from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_or_create_url


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_short_url(short):
    url_map = URLMap.query.filter_by(short=short).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def add_short_url():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    obj, created = get_or_create_url(data.get('url'), data.get('custom_id'))
    return jsonify(
        obj.to_dict()
    ), HTTPStatus.CREATED if created else HTTPStatus.OK
