from datetime import datetime, timezone

from flask import request

from . import db
from .constants import MAX_LINK_LEN, MAX_SHORT_LEN


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LINK_LEN), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LEN), unique=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            'url': self.original,
            'short_link': f'{request.host_url}{self.short}'
        }

    def from_dict(self, data):
        for field in ['original', 'short']:
            if field in data:
                setattr(self, field, data[field])
