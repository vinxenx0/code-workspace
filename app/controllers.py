# app/controllers.py
from .models import db, User

def init_app(app):
    db.init_app(app)

def create_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def update_user(user, username, password):
    user.username = username
    user.password = password
    db.session.commit()

def delete_user(user):
    db.session.delete(user)
    db.session.commit()