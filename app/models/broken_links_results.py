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
    anchor_text = db.Column(db.String(255))
    html_source = db.Column(db.LargeBinary)
    fast_mode = db.Column(db.Boolean)
    link_checker = db.Column(db.Boolean)
    spelling_checker = db.Column(db.Boolean)
    args = db.Column(db.String(255))

class DomainStats(db.Model):
    __tablename__ = 'DomainStats'  # Agrega esta línea para especificar el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    status_code = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    doctype_counts = db.Column(db.Text)
    urls_scanned = db.Column(db.Integer)
    broken_links = db.Column(db.Integer)
    redirect_links = db.Column(db.Integer)
    other_links = db.Column(db.Integer)
    start_time = db.Column(db.DATETIME)
    end_time = db.Column(db.DATETIME)
    total_time = db.Column(db.TIME)

