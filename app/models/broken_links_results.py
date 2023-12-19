# app/models/broken_links_results.py
from app import db

class Broken_Links_Results(db.Model):
    __tablename__ = 'ScanResults'  # Agrega esta línea para especificar el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    target_url = db.Column(db.String(255))
    scanned_url = db.Column(db.String(255))
    broken_url = db.Column(db.String(255))
    error_code = db.Column(db.Integer)
    fast_mode = db.Column(db.Boolean)
    link_checker = db.Column(db.Boolean)
    spelling_checker = db.Column(db.Boolean)
    args = db.Column(db.String(255))
