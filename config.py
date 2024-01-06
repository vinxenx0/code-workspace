# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.databases/app.db') #no se crea en el directorio
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:dldlt741@81.19.160.10/interec'

SQLALCHEMY_TRACK_MODIFICATIONS = False

IDS_ESCANEO = ['4b99956ba942f7986ccc2e5c992c3a2a111385bfdbbfa2223818c6a8d9e28510',
        '41038960d6084d0e2ba5416c0c2a52777cc40e119b7c69fb0aeaa4b8231cd2e0',
        '5b485f2d386e81e56d67e6f1663d7d965f69985e11d771e56b0caf6f5ecb0849'
           ]  # Reemplaza con los IDs específicos que se proporcionarán

SECRET_KEY = 'your_secret_key_here'

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = '.logs/app.log' #os.environ.get('LOG_FILE') #no se crea en el directorio