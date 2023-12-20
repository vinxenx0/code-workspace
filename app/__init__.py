# app/__init__.py

import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_talisman import Talisman
from flask_babel import Babel, _
#from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object('config')

# Configure logging
log_level = os.environ.get('LOG_LEVEL') or 'DEBUG'
# Configure logging in "paranoid" mode
log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(level=log_level, format=log_format)  # Setting level to 10 for DEBUG
# Get a logger for this module
logger = logging.getLogger(__name__)

# Set up a file handler with detailed format for logs
log_file = os.environ.get('LOG_FILE') or '.logs/app.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Add Talisman for security headers
csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'https://code.jquery.com',
        'https://cdn.jsdelivr.net',
        'https://maxcdn.bootstrapcdn.com',
        '/static/js/scripts.js',  # Include the external script source
    ],
    'style-src': [
        '\'self\'',
        'https://stackpath.bootstrapcdn.com',
        'https://fonts.googleapis.com',
    ],
    'script-src-elem': [
        '\'self\'',
        'https://code.jquery.com',
        'https://cdn.jsdelivr.net',
        'https://maxcdn.bootstrapcdn.com',
        '/static/js/scripts.js',
    ],
    'style-src-elem': [
        '\'self\'',
        'https://stackpath.bootstrapcdn.com',
        'https://fonts.googleapis.com',
        '/static/css/styles.css',
    ],
    # Add other directives as needed
}

Talisman(app, content_security_policy=None)



# Add Babel for i18n support
babel = Babel(app)
# Configure Babel
babel.init_app(app, default_locale='en')


# Add JWTManager for token-based authentication
#jwt = JWTManager(app)

from app.controllers import user_controller
from app.views import user_view
from app import db
from app.models.user_model import User
#from app.models.suggestions_model import Suggestion  

with app.app_context():
 
    db.create_all()
    if not User.query.first():
       
        # Create default users with hashed passwords and roles
        default_user = User(username='user', email='user@user.com', password=bcrypt.generate_password_hash('user').decode('utf-8'), role='user')
        default_admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='superadmin')

        # Add default users to the database
        db.session.add(default_user)
        db.session.add(default_admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import SECRET_KEY for CSRF protection
from config import SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY


# Error handling for common HTTP error codes
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Include the admin controller
from app.controllers import admin_controllers

# Function to check if the current user is an admin
def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'
app.jinja_env.globals.update(is_admin=is_admin)

# Add Bootstrap pagination script
app.jinja_env.globals.update(enumerate=enumerate)

from app.controllers import services_controller  # Add this line to import the new controller
from app.controllers import tools_controller  # Add this line to import the new controller


# import pdfkit

# pdfkit_config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')
# pdfkit.from_url('http://google.com', 'out.pdf', configuration=pdfkit_config)

