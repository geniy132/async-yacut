import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SWAGGER_URL = '/docs'
    API_URL = '/static/openapi.yml'
    DISK_TOKEN = os.getenv('DISK_TOKEN')
