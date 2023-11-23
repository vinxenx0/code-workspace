# app/views.py
import os
from flask import Flask, render_template, redirect, url_for, flash
from flask import request
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

# Elimina el campo 'role' del formulario UserForm
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
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

# Agrega la nueva ruta de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Se ha desconectado correctamente.', 'success')
    return redirect(url_for('index'))

# Actualiza la creación de usuarios en la ruta '/register'
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_authenticated and current_user.username != 'admin':
        flash('Solo los administradores pueden registrar nuevos usuarios.', 'danger')
        return redirect(url_for('index'))

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El usuario ya existe.', 'danger')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario registrado exitosamente.', 'success')
            return redirect(url_for('index'))

    return render_template('register.html', form=form)



# Nueva ruta para editar usuarios
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Asegurémonos de que solo el administrador puede editar cualquier usuario
    if current_user.username != 'admin':
        flash('Solo los administradores pueden editar usuarios.', 'danger')
        return redirect(url_for('index'))

    # Obtener el usuario de la base de datos
    user_to_edit = User.query.get(user_id)

    if not user_to_edit:
        flash('Usuario no encontrado.', 'danger')
        return render_template('index.html')

    form = UserForm(obj=user_to_edit)

    if request.method == 'POST' and form.validate_on_submit():
        # Actualizar la información del usuario
        form.populate_obj(user_to_edit)

        # Actualizar la contraseña solo si se proporciona un nuevo valor
        if form.password.data:
            user_to_edit.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('index'))

    # Método GET: Mostrar el formulario de edición
    return render_template('edit_user.html', form=form, user=user_to_edit)



@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    # Obtener el usuario de la base de datos
    user_to_delete = User.query.get(user_id)
    
    # Asegúrate de que solo el usuario logueado pueda eliminar su propia cuenta
    if current_user.username != 'admin':
        flash('No tienes permisos para eliminar esta cuenta.', 'danger')
        return redirect(url_for('index'))

    

    if not user_to_delete:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Eliminar usuario de la base de datos
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'success')
        return redirect(url_for('index'))

    return render_template('delete_user.html', user_id=user_id)


@app.route('/option1')
@login_required
def option1():
    return render_template('option1.html')

@app.route('/option2')
@login_required
def option2():
    return render_template('option2.html')

@app.route('/option3')
@login_required
def option3():
    return render_template('option3.html')

@app.route('/option4')
@login_required
def option4():
    return render_template('option4.html')