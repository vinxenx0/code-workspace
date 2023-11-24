# app/__init__.py

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

Talisman(app, content_security_policy=None)

from app.controllers import user_controller
from app.views import user_view
from app import db
from app.models.user_model import User

with app.app_context():
    db.create_all()
    if not User.query.first():
        # Create default users with hashed passwords and roles
        default_user = User(username='user', email='user@user.com', password=bcrypt.generate_password_hash('user').decode('utf-8'), role='user')
        default_admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash('admin').decode('utf-8'), role='admin')

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