import random
import re
import string

from . import db
from .constants import (
    ALLOWED_CHARS,
    FORBIDDEN_IDS,
    MAX_SHORT_ID_LEN,
    RANDOM_ID_LEN,
    ERROR_INVALID_NAME,
    ERROR_ALREADY_EXISTS
)
from .error_handlers import InvalidAPIUsage
from .models import URLMap


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
