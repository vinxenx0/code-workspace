# app/controllers/user_controller.py

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.models.user_model import User
from app.views.user_view import UserProfileForm, LoginForm


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('list_users'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('list_users'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Adjust the number of users per page as needed
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/list.html', users=users)

# ... other routes ...


@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_authenticated and (current_user == user or current_user.role == 'admin'):
        return render_template('user/profile.html', user=user)
    else:
        flash('Permission denied. You can only view your own profile.', 'danger')
        return redirect(url_for('list_users'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Permission denied. Only admins can add users.', 'danger')
        return redirect(url_for('list_users'))

    form = UserProfileForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)

        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('user/add.html', form=form)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user)  # Pre-populate the form with the existing user data
    if form.validate_on_submit():
        form.populate_obj(user)  # Update the user object with the form data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('user/edit.html', form=form, user=user)


@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))


