# app/models/suggestion.py

from datetime import datetime
from app import db

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    error_type = db.Column(db.String(50), nullable=False)
    origin_page = db.Column(db.String(50), nullable=False)
    suggestions = db.Column(db.Text, nullable=True)