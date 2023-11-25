# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'your_secret_key_here'

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = 'app.log' #os.environ.get('LOG_FILE')