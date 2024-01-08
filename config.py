# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.databases/app.db') #no se crea en el directorio
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:dldlt741@81.19.160.10/interec'

SQLALCHEMY_TRACK_MODIFICATIONS = False

IDS_ESCANEO = ['29f2a2bdfff2730fcdd8a5e6e6885b7f0d2445f7b9cacca3aa813fc074c5ccdd',
        '2f47060f663cdd0bc988faf1825d23181f31f5d54aaff94a5f637ef21d33b1aa',
        'd8876252d72462e4de9333d0d5a1884a21f9e0be63bf88f992950646cdb0ed33'
        #'600ce9cb0f56f949d30bf6004076a2aa541f22b5ae6c2381137bc2937733a506'
           ]  # Reemplaza con los IDs específicos que se proporcionarán

SECRET_KEY = 'your_secret_key_here'

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

LOG_LEVEL = 'DEBUG' #os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = '.logs/app.log' #os.environ.get('LOG_FILE') #no se crea en el directorio