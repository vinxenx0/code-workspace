from app import db
from datetime import datetime
from sqlalchemy import func, create_engine, Column, Integer, String, Text, DateTime, JSON, desc, update, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import LargeBinary

class Resultado(db.Model):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_escaneo = Column(DateTime, default=datetime.now)
    dominio = Column(String(255))
    codigo_respuesta = Column(Integer)
    tiempo_respuesta = Column(Integer)
    pagina = Column(String(1383))
    parent_url = Column(String(1383))
    meta_tags = Column(JSON)
    heading_tags = Column(JSON)
    imagenes = Column(JSON)
    enlaces_totales = Column(Integer)
    enlaces_inseguros = Column(Integer)
    tipos_archivos = Column(JSON)
    errores_ortograficos = Column(JSON)
    num_errores_ortograficos = Column(Integer)
    num_redirecciones = Column(Integer)
    alt_vacias = Column(Integer)
    num_palabras = Column(Integer)
    e_title = Column(Integer)
    e_head = Column(Integer)
    e_body = Column(Integer)
    e_html = Column(Integer)
    e_robots = Column(Integer)
    e_description = Column(Integer)
    e_keywords = Column(Integer)
    e_viewport = Column(Integer)
    e_charset = Column(Integer)
    html_valid = Column(Integer)
    content_valid = Column(Integer)
    responsive_valid = Column(Integer)
    image_types = Column(JSON)
    wcagaaa = Column(JSON)
    valid_aaa = Column(Integer)
    lang = Column(String(10))
    title_long = Column(String(1383))
    title_short = Column(String(1383))
    title_duplicate = Column(String(1383))
    desc_long = Column(String(1383))
    desc_short = Column(String(1383))
    h1_duplicate = Column(Integer)
    images_1MB = Column(Integer)
    html_copy = Column(LargeBinary)
    id_escaneo = Column(String(255), nullable=False)
    peso_total_pagina = Column(Integer)


# Definir el modelo de la tabla "sumario"
class Sumario(db.Model):
    __tablename__ = 'sumario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dominio = Column(String(255))
    total_paginas = Column(Integer)
    duracion_total = Column(Integer)
    codigos_respuesta = Column(JSON)
    hora_inicio = Column(String(20))
    hora_fin = Column(String(20))
    fecha = Column(String(10))
    html_valid_count = Column(Integer)
    content_valid_count = Column(Integer)
    responsive_valid_count = Column(Integer)
    valid_aaaa_pages = Column(Integer)
    idiomas = Column(JSON)
    paginas_inseguras = Column(Integer)  # Nuevo campo
    total_404 = Column(Integer)  # Nuevo campo
    enlaces_inseguros = Column(Integer)
    pages_title_long = Column(Integer)  # Nuevos campos
    pages_title_short = Column(Integer)
    pages_title_dup = Column(Integer)
    pages_desc_long = Column(Integer)
    pages_desc_short = Column(Integer)
    pages_h1_dup = Column(Integer)
    pages_img_1mb = Column(Integer)
    id_escaneo = Column(String(255), nullable=False)
    #id_escaneo = Column(Integer, ForeignKey('escaneo.id'))
    tiempo_medio = Column(Float)
    pages_err_orto = Column(Integer)
    peso_total_paginas = Column(Integer)