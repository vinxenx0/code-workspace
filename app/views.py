# app/views.py
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .controllers import create_user, get_all_users, get_user_by_id, update_user, delete_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # + os.path.join(app.instance_path, 'site.db')
app.config['SECRET_KEY'] = 'your_secret_key'  # Cambia esto a una clave secreta segura
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Formulario para la creación de usuarios
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required  # Requiere que el usuario esté autenticado para acceder a esta ruta
def index():
    users = get_all_users()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Inicio de sesión fallido. Verifica tus credenciales', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required  # Requiere que el usuario esté autenticado para acceder a esta ruta
def logout():
    logout_user()
    return redirect(url_for('index'))
