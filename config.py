# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.databases/app.db') #no se crea en el directorio
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:dldlt741@81.19.160.10/interec' #mc_mutual_scans'

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'your_secret_key_here'

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = '.logs/app.log' #os.environ.get('LOG_FILE') #no se crea en el directorio

# IDs de escaneo específicos
IDS_ESCANEO = [
    '53095f2ed01c1f689494ecef6867fff33a105162639953832dc1ba33fa528cd6',
    'f832e71fe746e702f7daf5891363258363ddb84b831dca989d42783589444e93',
    '9cc4a2614878159a57a3b76b5e122b0c65b46300706874e14774697fe726615e'
]
