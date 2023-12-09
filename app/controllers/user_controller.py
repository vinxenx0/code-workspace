# app/controllers/user_controller.py

import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.models.user_model import User
from app.views.user_view import UserProfileForm, LoginForm
from sqlalchemy.exc import IntegrityError
from flask_babel import g, _
from app.models.suggestions_model import Suggestion

# Get a logger for this module
logger = logging.getLogger(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.role not in ['admin', 'superadmin']:
                return redirect(url_for('admin'))
            next_page = request.args.get('next')
            flash('Acceso correcto!', 'success')
            logger.info(f"Usuario {user.username} se ha identificado.")
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Acceso fallido, comprueba email y contraseña.', 'danger')
            logger.error("Invalid login attempt.")
    return render_template('user/login.html', form=form)

@app.route('/admin')
@login_required
def admin():
    if current_user.role not in ['admin', 'superadmin']:
        flash(_('No tienes permisos para acceder a esta pagina..'), 'danger')
        return redirect(url_for('index'))
    
    # Your admin-specific logic here
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Adjust the number of users per page as needed
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/admin.html', users=users)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('user/logout.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/suggestions')
@login_required
def list_suggestions():
    suggestions = Suggestion.query.all()
    return render_template('user/suggestions.html', suggestions=suggestions)

@app.route('/list_users')
@login_required
def list_users():
    #if current_user.role not in ['admin', 'superadmin']:
    #    flash('Permission Denied. You do not have access to this page.', 'danger')
    #    return redirect(url_for('home'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Adjust the number of users per page as needed
    order_by = request.args.get('order_by', 'created_at')  # Default order by created_at
    users = User.query.order_by(db.desc(getattr(User, order_by))).all()
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/list.html', users=users, order_by=order_by)


# ... other routes ...


@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_authenticated and (current_user == user or current_user.role == 'admin' or current_user.role == 'superadmin'):
        return render_template('user/profile.html', user=user)
    else:
        flash('Permiso denegado. Solo puede ver tu propio perfil.', 'danger')
        return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role not in ['admin', 'superadmin']:
        flash('Solo administradores pueden añadir usuarios.', 'danger')
        return redirect(url_for('index'))

    form = UserProfileForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario nuevo añadido correctamente!', 'success')
        logger.debug(f"User {new_user.username} created.")
        return redirect(url_for('admin'))
    return render_template('user/add.html', form=form)


#@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
#@login_required
#def edit_user(user_id):
#    user = User.query.get_or_404(user_id)
#    form = UserProfileForm(obj=user)  # Pre-populate the form with the existing user data
#    if form.validate_on_submit():
#        form.populate_obj(user)  # Update the user object with the form data
#        user.updated_at = db.func.current_timestamp()
#        db.session.commit()
#        flash('User updated successfully!', 'success')
#        return redirect(url_for('admin'))
#    return render_template('user/edit.html', form=form, user=user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user)  # Pre-populate the form with the existing user data
    if form.validate_on_submit():
        # Check if the new username is unique before updating
        new_username = form.username.data
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            flash('Ese nombre ya existe, elije otro.', 'danger')
            return render_template('user/edit.html', form=form, user=user)

        # Update the user object with the form data
        form.populate_obj(user)
        user.updated_at = db.func.current_timestamp()

        try:
            db.session.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Ha ocurrido un error, intentalo de nuevo.', 'danger')
            app.logger.error(f"IntegrityError during user update: {e}")

    return render_template('user/edit.html', form=form, user=user)


@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash('Usuario borrado correctamente', 'success')
        return redirect(url_for('admin'))
    return render_template('user/delete.html', user=user)

@app.route('/set_locale', methods=['POST'])
def set_locale():
    if current_user.is_authenticated:
        current_user.locale = request.form['language']
        db.session.commit()
    g.locale = request.form['language']
    return redirect(request.referrer)

# app/controllers/user_controller.py