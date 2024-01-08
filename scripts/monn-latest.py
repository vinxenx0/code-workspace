# peso pagina descargada y los tipos de archivo
# tipo html o pdf (is pdf)
# e_nav 

# (c) vicente b. lopez plaza
# vinxenxo@protonmail.com 

import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
import time
import string
from PIL import Image
from io import BytesIO
import os
import json
import imghdr
import subprocess
from collections import Counter
from lxml import etree
from urllib.parse import urlparse, urljoin
import aspell
import string
import langid
from sqlalchemy import func, create_engine, Column, Integer, String, Text, DateTime, JSON, desc, update, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import LargeBinary
import secrets
import logging


# Definir el modelo de la tabla "resultados"
Base = declarative_base()
class Resultado(Base):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_escaneo = Column(DateTime, default=datetime.now)
    dominio = Column(String(255))
    codigo_respuesta = Column(Integer)
    tiempo_respuesta = Column(Float) #Column(Integer)
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
    html_copy = Column(Text)
    html_copy_dos = Column(Text)
    id_escaneo = Column(String(255), nullable=False)
    peso_total_pagina = Column(Integer)
    is_pdf = Column(Integer)


# Definir el modelo de la tabla "sumario"
class Sumario(Base):
    __tablename__ = 'sumario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dominio = Column(String(255))
    total_paginas = Column(Float)
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
    pages_alt_vacias = Column(Integer)
    peso_total_paginas = Column(Integer)
    pdf_count = Column(Integer)
    html_count = Column(Integer)
    others_count = Column(Integer)
    

def guardar_en_resultados(session, resultado):

    try:
        session.add(resultado)
        session.commit()
    except OperationalError as e:
        print(f"Error de conexión: {e}")
        session.rollback()
        session = Session()
        guardar_en_resultados(session, resultado)
    finally:
        session.flush()

# FunciÃ³n para guardar un sumario en la tabla "sumario"
def guardar_en_sumario(session, sumario):
    try:
        #session = Session()
        session.add(sumario)
        session.commit()
    except OperationalError as e:
        print(f"Error de conexión: {e}")
        # Realizar reconexión y volver a intentar
        session.rollback()
        session = Session()  # Asegúrate de configurar la sesión según tus necesidades
        guardar_en_sumario(session, sumario)
    finally:
        #print("Guardado sumario")
        session.flush()

def extraer_texto_visible(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    visible_text = ' '.join(soup.stripped_strings)
    return visible_text


def detectar_idioma(texto):
    try:
        idioma, _ = langid.classify(texto)
        return idioma
    except Exception as e:
        print(f"Error al detectar el idioma: {e}")
        return None
    

def analizar_ortografia(texto, idiomas=['es', 'fr', 'en', 'ca']):
    errores_ortograficos = None  # Inicializa como None en lugar de una lista vacía
    palabras = set()  # Usamos un conjunto para almacenar las palabras únicas

    idioma_detectado = detectar_idioma(texto)
    if idioma_detectado and idioma_detectado in idiomas:
        try:
            speller = aspell.Speller('lang', idioma_detectado)

            # Eliminar números y símbolos de moneda, así como exclamaciones, interrogaciones y caracteres similares
            translator = str.maketrans('', '', string.digits + string.punctuation + '¡!¿?')
            texto_limpio = texto.translate(translator)

            palabras_excluidas = {'MUTUAL', 'MC-MUTUAL', 'cookies'}
            palabras_excluidas.update({'Zonnox','VoIP','Home','Garum','Murex','Distwin','LealtyCard','MiGasolinera','4GL'})
            redes_sociales = {
                'facebook', 'twitter', 'instagram', 'linkedin', 'pinterest', 'snapchat', 'tiktok', 'youtube',
                'whatsapp', 'telegram', 'reddit', 'tumblr', 'flickr', 'vimeo', 'myspace', 'google+', 'wechat',
                'wechat', 'weibo', 'xing', 'vk', 'renren', 'badoo', 'hi5', 'orkut', 'friendster'
            }

            provincias_espanolas = {
                'madrid', 'barcelona', 'valencia', 'sevilla', 'zaragoza', 'malaga', 'murcia', 'palma', 'bilbao',
                'alicante', 'cordoba', 'valladolid', 'vigo', 'gijon', 'hospitalet', 'coruna', 'vitoria', 'granada',
                'elche', 'oviedo', 'sabadell', 'santa cruz', 'pamplona', 'cartagena'
            }
            
            comunidades_autonomas_espanolas = {
                'andalucia', 'aragon', 'asturias', 'baleares', 'canarias', 'cantabria', 'castilla la mancha',
                'castilla y leon', 'cataluna', 'extremadura', 'galicia', 'madrid', 'murcia', 'navarra',
                'pais vasco', 'la rioja', 'comunidad valenciana'
            }

            palabras_excluidas.update(redes_sociales)
            palabras_excluidas.update(provincias_espanolas)
            palabras_excluidas.update(comunidades_autonomas_espanolas)

            # Agrega palabras personalizadas excluidas
            palabras = {palabra for palabra in texto_limpio.split() if palabra.lower() not in palabras_excluidas and len(palabra) >= 4}

            # Filtra palabras que tengan TODOS los signos de puntuación, interrogación, exclamación, caracteres especiales o símbolos de moneda
            caracteres_especiales = string.punctuation + '¡!¿?$€£@#%^&*()_-+=[]{}|;:,.<>/"'
            palabras = {palabra for palabra in palabras if not all(c in caracteres_especiales for c in palabra)}

            # Errores ortográficos solo para palabras que no están en la lista excluida y no cumplen con el chequeo del speller
            errores_ortograficos = [palabra for palabra in palabras if not speller.check(palabra)]

        except Exception as e:
            print(f"Error al procesar el idioma {idioma_detectado}: {e}")

    return list(errores_ortograficos)



def extraer_meta_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_tags_info = [{'name': tag.get('name'), 'content': tag.get('content')} for tag in meta_tags]
    return meta_tags_info

def analizar_heading_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    heading_tags_count = {tag: len(soup.find_all(tag)) for tag in heading_tags}
   
    # Contar las veces que aparece la etiqueta h1 específicamente
    h1_duplicate = heading_tags_count.get('h1', 0)

    return heading_tags_count, h1_duplicate



def extraer_informacion_imagenes(response_text, base_url):
    soup = BeautifulSoup(response_text, 'html.parser')
    img_tags = soup.find_all('img')
    info_imagenes = []
    image_types = []
    images_1MB = 0

    for img_tag in img_tags:
        src = img_tag.get('src')
        alt = img_tag.get('alt', '')
        src_url = urljoin(base_url, src)

        try:
            response = requests.get(src_url, stream=True)
            response.raise_for_status()

            # Get the filename, size in MB, and check if the image is broken
            filename = urlparse(src_url).path.split("/")[-1]
            size_mb = len(response.content) / (1024 * 1024)
            is_broken = False
            
            # Nuevo campo
            if size_mb > 1:
                images_1MB += 1

            # Check if the image is broken by opening it with PIL
            try:
                Image.open(BytesIO(response.content))
            except Exception as e:
                is_broken = True

            # Get the image type
            image_type = imghdr.what(None, h=response.content)

            info_imagen = {
                'filename': filename,
                'size_mb': size_mb,
                'url': src_url,
                'alt_text': alt,
                'broken': is_broken,
                'image_type': image_type
            }

            info_imagenes.append(info_imagen)
            image_types.append(image_type)
        except Exception as e:
            print(f"Error al obtener informaciÃ³n de la imagen {src_url}: {str(e)}")

    return info_imagenes, image_types, images_1MB

def contar_alt_vacias(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    img_tags = soup.find_all('img', alt='')

    return len(img_tags)

def contar_enlaces(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    enlaces = soup.find_all('a', href=True)
    enlaces_inseguros = [enlace['href'] for enlace in enlaces if enlace['href'].startswith('http://')]
    return len(enlaces), len(enlaces_inseguros)


def contar_tipos_archivos(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    archivos = soup.find_all(['a', 'img', 'video', 'audio', 'source', 'link', 'script'], href=True, src=True)
    tipos_archivos = {'pdf': 0, 'video': 0, 'sound': 0, 'image': 0, 'app': 0, 'others': 0}
    peso_total = 0  # Nuevo campo

    for archivo in archivos:
        url_archivo = archivo.get('href') or archivo.get('src')
        extension = url_archivo.split('.')[-1].lower()

        if extension == 'pdf':
            tipos_archivos['pdf'] += 1
        elif extension in ['mp4', 'avi', 'mkv', 'mov']:
            tipos_archivos['video'] += 1
        elif extension in ['mp3', 'wav', 'ogg']:
            tipos_archivos['sound'] += 1
        elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            tipos_archivos['image'] += 1
            # Obtener el peso de la imagen y sumarlo al peso total
            peso_total += obtener_peso_archivo(url_archivo)
        elif extension in ['apk', 'exe', 'msi']:
            tipos_archivos['app'] += 1
        else:
            tipos_archivos['others'] += 1

    tipos_archivos['peso_total'] = peso_total  # Nuevo campo
    return tipos_archivos


def obtener_peso_archivo(url_archivo):
    try:
        response = requests.head(url_archivo, allow_redirects=True)
        if response.status_code == 200:
            # Calcular el peso en kilobytes
            peso_kb = int(response.headers.get('content-length', 0)) / 1024
            return peso_kb
    except Exception as e:
        print(f"Error al obtener el peso del archivo {url_archivo}: {str(e)}")
    return 0


def es_html_valido(html_text):
    try:
        parser = etree.HTMLParser()
        etree.fromstring(html_text, parser)
        return True
    except Exception as e:
        return False

# es necesaria?
def contar_redirecciones(url, max_redirecciones=10):
    count = 0
    current_url = url
    redireccion_tipo = 'Desconocido'  # Valor predeterminado

    while count < max_redirecciones:
        try:
            response = requests.head(current_url, allow_redirects=True)
            if response.status_code // 100 == 3:
                redireccion_tipo = obtener_tipo_redireccion(response.status_code)
                current_url = response.headers['Location']
                count += 1
            else:
                break
        except Exception as e:
            print(f"Error al contar redirecciones para {url}: {str(e)}")
            break

    return count, redireccion_tipo

# Sigue sin contarlos?
def obtener_tipo_redireccion(status_code):
    if status_code == 301:
        return 'RedirecciÃ³n permanente (301)'
    elif status_code == 302:
        return 'RedirecciÃ³n temporal (302)'
    elif status_code == 303:
        return 'RedirecciÃ³n de otro recurso (303)'
    elif status_code == 307:
        return 'RedirecciÃ³n temporal (307)'
    elif status_code == 308:
        return 'RedirecciÃ³n permanente (308)'
    else:
        return 'Desconocido'
    
    
def contar_palabras_visibles(response_text):
    visible_text = extraer_texto_visible(response_text)
    palabras = visible_text.split()
    return len(palabras)

# Modificaciones en analizar_meta_tags
def analizar_meta_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    meta_tags_info = {
        'e_title': False,
        'e_head': False,
        'e_body': False,
        'e_html': False,
        'e_robots': False,
        'e_description': False,
        'e_keywords': False,
        'e_viewport': False,
        'e_charset': False,
        'title_long': False,
        'title_short': False,
        'title_duplicate': False,
        'desc_short': False,
        'desc_long': False
    }

    title_content = None
    desc_content = None

    # Obtener las etiquetas específicas
    body_tag = soup.find('body')
    title_tag = soup.find('title')
    head_tag = soup.find('head')
    html_tag = soup.find('html')
    robots_tag = soup.find('meta', attrs={'name': 'robots'})
    description_tag = soup.find('meta', attrs={'name': 'description'})
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
    charset_tag = soup.find('meta', attrs={'charset': True})

    # Verificar la existencia de las etiquetas y actualizar el diccionario
    meta_tags_info['e_title'] = 1 if title_tag else 0
    meta_tags_info['e_head'] = 1 if head_tag else 0
    meta_tags_info['e_body'] = 1 if body_tag else 0
    meta_tags_info['e_html'] = 1 if html_tag else 0
    meta_tags_info['e_robots'] = 1 if robots_tag else 0
    meta_tags_info['e_description'] = 1 if description_tag else 0
    meta_tags_info['e_keywords'] = 1 if keywords_tag else 0
    meta_tags_info['e_viewport'] = 1 if viewport_tag else 0
    meta_tags_info['e_charset'] = 1 if charset_tag else 0
    


    for tag in soup.find_all('meta'):
        tag_name = tag.get('name', '').lower()
        tag_content = tag.get('content', '').lower()

        if tag_name in meta_tags_info:
            meta_tags_info[tag_name] = 1
        elif tag_content in meta_tags_info:
            meta_tags_info[tag_content] = 1

    if tag_name == 'title':
        title_content = tag_content
    elif tag_name == 'description':
        desc_content = tag_content

    # Nuevos campos
    if title_tag:
        title_content = title_tag.get_text().lower()
        if len(title_content) > 150:
            meta_tags_info['title_long'] = title_content
        elif len(title_content) < 50:
            meta_tags_info['title_short'] = title_content

        # Verificar duplicados en title
        if title_content in response_text[len(title_content):]:
            meta_tags_info['title_duplicate'] = title_content

    if description_tag:
        desc_content = description_tag.get('content', '').lower()
        if len(desc_content) > 150:
            meta_tags_info['desc_long'] = desc_content
        elif len(desc_content) < 50:
            meta_tags_info['desc_short'] = desc_content

    return meta_tags_info



def es_html_valido(response_text):
    try:
        soup = BeautifulSoup(response_text, 'html.parser')
        return bool(soup.html and soup.head and soup.title and soup.body)
    except Exception as e:
        return False


def es_contenido_valido(response_text):
    try:
        soup = BeautifulSoup(response_text, 'html.parser')
        return bool(soup.h1 and soup.h2 and soup.h3)
    except Exception as e:
        return False


def es_responsive_valid(response_text):
    try:
        soup = BeautifulSoup(response_text, 'html.parser')
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        return viewport_tag is not None
    except Exception as e:
        return False



def ejecutar_pa11y(url_actual):
    try:
        # Ejecuta pa11y y captura la salida directamente
        command = f"pa11y --standard WCAG2AAA  --ignore issue-code-1 --ignore issue-code-2 --reporter csv {url_actual}"
        process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Imprime la salida estÃ¡ndar y la salida de error de pa11y
        #print("pa11y stdout:")
        #print(process.stdout)
        #print("pa11y stderr:")
        #print(process.stderr)

        # Verifica si el cÃ³digo de salida es diferente de cero (error)
        if process.returncode != 0:
            print(f"pa11y devolviÃ³ un cÃ³digo de salida no nulo {process.returncode}")
            return []  # Devuelve una lista vacÃ­a en caso de error

        # Obtiene la salida del comando pa11y (sin la primera lÃ­nea que es la cabecera)
        pa11y_results_lines = process.stdout.strip().split('\n')[1:]

        # Reformatea los resultados de pa11y en una lista de objetos
        pa11y_results_list = []
        for line in pa11y_results_lines:
            fields = line.split('","')
            if len(fields) == 5:
                pa11y_results_list.append({
                    "type": fields[0].strip('"'),
                    "code": fields[1].strip('"'),
                    "message": fields[2].strip('"'),
                    "context": fields[3].strip('"'),
                    "selector": fields[4].strip('"')
                })

        # Verifica si el resultado de pa11y contiene datos
        return pa11y_results_list
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar pa11y para {url_actual}: {e}")
        return []  # Devuelve una lista vacÃ­a en caso de error



def escanear_dominio(url_dominio, exclusiones=[], extensiones_excluidas=[]):
    resultados = []
    dominio_base = urlparse(url_dominio).netloc
    urls_por_escanear = [(url_dominio, None)]
    urls_escaneadas = set()
    
    pdf_count = 0  # Contador para el total de PDFs rastreados


    while urls_por_escanear:
        url_actual, parent_url = urls_por_escanear.pop()

        if url_actual in urls_escaneadas:
            continue

        # ComprobaciÃ³n de exclusiones antes de la solicitud HTTP
        if any(patron in url_actual for patron in exclusiones) or any(ext in url_actual for ext in extensiones_excluidas):
            urls_escaneadas.add(url_actual)
            continue

        try:
            response = requests.get(url_actual, timeout=180)
            tiempo_respuesta = response.elapsed.total_seconds()
            codigo_respuesta = response.status_code

            resultados_pagina = {
                'fecha_escaneo': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dominio': dominio_base,
                'codigo_respuesta': codigo_respuesta,
                'tiempo_respuesta': tiempo_respuesta,
                'pagina': url_actual,
                'parent_url': parent_url,
                # Python 'tuple' cannot be converted to a MySQL type
                'num_redirecciones': 0, #contar_redirecciones(url_actual)
                'title_long': False,
                'title_short': False,
                'title_duplicate': False,
                'desc_long': False,
                'desc_short': False,
                'h1_duplicate': False,  # Nuevo campo
                'images_1MB': False,  # Nuevo campo
                'id_escaneo': id_escaneo,
                'tipos_archivos': False,
                'peso_total_pagina': 0,
                'is_pdf': -1  # Nuevo campo para indicar si la página es un PDF
       
            }

            if codigo_respuesta == 200:
                 #if codigo_respuesta == 200 and response.headers['content-type'].startswith('text/html'):
            #    if es_html_valido(response.text):
                if 'pdf' in url_actual.lower():  # Comprobar si la URL contiene '%pdf%'
                    resultados_pagina['is_pdf'] = 1
                    pdf_count += 1
                    resultados.append(resultados_pagina)
                    continue  # Si es un PDF, no analizar y pasar a la siguiente URL

                
                resultados_pagina['is_pdf'] = 0 # otros
                
                if response.headers['content-type'].startswith('text/html'):
                    if es_html_valido(response.text):
                        
                        print(f"Escanenado: {url_actual}")
            
           
                        resultados_pagina['enlaces_totales'] = 0  # Inicializar en 0
                        resultados_pagina['enlaces_inseguros'] = 0  # Inicializar en 0
                                

                        meta_tags_info = extraer_meta_tags(response.text) or {}
                        resultados_pagina['meta_tags'] = meta_tags_info

                        meta_tags_revision = analizar_meta_tags(response.text)
                        resultados_pagina.update(meta_tags_revision)

                        if meta_tags_revision['title_long']:
                            resultados_pagina['title_long'] = meta_tags_revision['title_long']
                        if meta_tags_revision['title_short']:
                            resultados_pagina['title_short'] = meta_tags_revision['title_short']
                        if meta_tags_revision['title_duplicate']:
                            resultados_pagina['title_duplicate'] = meta_tags_revision['title_duplicate']
                        if meta_tags_revision['desc_long']:
                            resultados_pagina['desc_long'] = meta_tags_revision['desc_long']
                        if meta_tags_revision['desc_short']:
                            resultados_pagina['desc_short'] = meta_tags_revision['desc_short']


                        heading_tags_count, h1_duplicate = analizar_heading_tags(response.text) #,h1_duplicate
                        resultados_pagina['heading_tags'] = heading_tags_count or {}
                        resultados_pagina['h1_duplicate'] = h1_duplicate

                        info_imagenes, image_types, images_1MB = extraer_informacion_imagenes(response.text, url_actual) #images_1MB
                        resultados_pagina['imagenes'] = info_imagenes or []
                        resultados_pagina['alt_vacias'] = contar_alt_vacias(response.text)
                        resultados_pagina['num_palabras'] = contar_palabras_visibles(response.text)

                        enlaces_totales, enlaces_inseguros = contar_enlaces(response.text)
                        resultados_pagina['enlaces_totales'] = enlaces_totales
                        resultados_pagina['enlaces_inseguros'] = enlaces_inseguros

                        resultados_pagina['images_1MB'] = images_1MB

                    
                        tipos_archivos = contar_tipos_archivos(response.text)
                        resultados_pagina['tipos_archivos'] = tipos_archivos
                        resultados_pagina['peso_total_pagina'] = tipos_archivos.get('peso_total', 0)


                        texto_visible = extraer_texto_visible(response.text)
                        errores_ortograficos = analizar_ortografia(texto_visible)
                        resultados_pagina['errores_ortograficos'] = errores_ortograficos
                        resultados_pagina['num_errores_ortograficos'] = len(errores_ortograficos)

                        resultados_pagina['lang'] = detectar_idioma(response.text)

                        # Nuevos campos de revisiÃ³n
                        meta_tags_revision = analizar_meta_tags(response.text)
                        resultados_pagina.update(meta_tags_revision)

                        resultados_pagina['html_valid'] = es_html_valido(response.text)
                        resultados_pagina['content_valid'] = es_contenido_valido(response.text)
                        resultados_pagina['responsive_valid'] = es_responsive_valid(response.text)

                        # Actualizar los campos a True si las validaciones son exitosas
                        if resultados_pagina['html_valid']:
                            resultados_pagina['e_html'] = True
                        if resultados_pagina['content_valid']:
                            resultados_pagina['e_body'] = True
                        if resultados_pagina['responsive_valid']:
                            resultados_pagina['e_viewport'] = True

                        # Contar las veces que se repiten los diferentes tipos de formato de imagen
                        image_types_count = Counter(image_types)
                        resultados_pagina['image_types'] = image_types_count

                        # Ejecutar pa11y y obtener resultados WCAG AAA
                        pa11y_results_csv = ejecutar_pa11y(url_actual)

                        # Antes de la inserción en la base de datos
                        resultados_pagina['wcagaaa'] = pa11y_results_csv
                        #resultados_pagina['wcagaaa'] = {'pa11y_results': pa11y_results_csv}
                        #resultados_pagina['wcagaaa']['pa11y_results'] = list(pa11y_results_csv)
                        #resultados_pagina['wcagaaa'] = {'pa11y_results': pa11y_results_csv}
                        resultados_pagina['valid_aaa'] = not pa11y_results_csv  # True si no hay recomendaciones, False en caso contrario
                        
                        resultados_pagina['is_pdf'] = 2 # es un html
                

            resultados.append(resultados_pagina)

            soup = BeautifulSoup(response.text, 'html.parser')
            enlaces = [urljoin(url_actual, a['href']) for a in soup.find_all('a', href=True)]


            enlaces_filtrados = [(enlace, url_actual) for enlace in enlaces
                                 if urlparse(enlace).netloc == dominio_base
                                 and not any(patron in enlace for patron in exclusiones)
                                 and not any(enlace.endswith(ext) for ext in extensiones_excluidas)]

            urls_por_escanear.extend(enlaces_filtrados)
        except Exception as e:
            print(f"Error al escanear {url_actual}: {str(e)}")

        urls_escaneadas.add(url_actual)
    

    return resultados



def generar_informe_resumen(resumen, nombre_archivo):
    header_present = os.path.exists(nombre_archivo)
    
    idiomas_encontrados = Counter()
    total_404 = Counter()
    total_enlaces_inseguros = Counter()
    paginas_inseguras = Counter()


    with open(nombre_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)

        if not header_present:
            escritor_csv.writerow(['dominio', 'total_paginas', 'duracion_total',
                                   'codigos_respuesta', 'hora_inicio', 'hora_fin', 'fecha',
                                   'html_valid_count', 'content_valid_count', 'responsive_valid_count',
                                   'valid_aaaa_pages', 'idiomas', 'paginas_inseguras', 'total_404','total_enlaces_inseguros',
                                   'pages_title_long', 'pages_title_short', 'pages_title_dup', 'pages_desc_long',
                                   'pages_desc_short', 'pages_h1_dup', 'pages_img_1mb','id_escaneo',
                                   'tiempo_medio','pages_err_orto','pages_alt_vacias','peso_total_paginas','pdf_count','html_count','others_count'])  # Agregar nuevos campos

        for dominio, datos in resumen.items():
            #print(f'Dominio: {dominio}, Datos: {datos}')
            total_404 = 0
            paginas_inseguras = 0
            total_enlaces_inseguros = 0
            html_valid_count = 0
            content_valid_count = 0
            responsive_valid_count = 0
            valid_aaaa_pages = 0  # Contador para pÃ¡ginas con 'valid_aaa' True
            codigos_respuesta = datos['codigos_respuesta']
            total_paginas = datos['total_paginas']
            duracion_total = datos['duracion_total']
            id_escaneo = datos['id_escaneo']
            #paginas_inseguras = sum(pagina.get('enlaces_inseguros', 0) > 0 for pagina in datos.get('paginas', []))
            total_404 = sum(pagina.get('codigo_respuesta', 0) == 404 for pagina in datos.get('paginas', []))
            tiempo_medio = 0 #(sum(pagina.get('tiempo_respuesta', 0) for pagina in datos.get('paginas', []))) / (total_paginas)
            pages_err_orto = 0
            pages_alt_vacias = 0
            peso_total_paginas = 0
            pdf_count = 0
            html_count = 0
            others_count = 0
            
            #for pagina in datos.get('paginas', []):
            #print(resultados_dominio)
            for pagina in resultados_dominio :
                total_enlaces_inseguros += pagina.get('enlaces_inseguros')
                peso_total_paginas += pagina.get('peso_total_pagina')
                
                if pagina.get('is_pdf') == 1:
                        pdf_count += 1
                
                if pagina.get('is_pdf') == 2:
                        html_count += 1
                
                if pagina.get('is_pdf') == 0:
                        others_count += 1
                
                
                if pagina.get('alt_vacias') >= 1:
                        pages_alt_vacias += 1
                        
                if pagina.get('num_errores_ortograficos') >= 1:
                        pages_err_orto += 1

                if pagina.get('codigo_respuesta') == 404:
                    total_404 += 1

                if pagina.get('enlaces_inseguros') >=  1:
                    paginas_inseguras += 1

                lang = pagina.get('lang')
                if lang:
                    idiomas_encontrados[lang] += 1

                html_valid_count += bool(pagina.get('html_valid', False))
                content_valid_count += bool(pagina.get('content_valid', False))
                responsive_valid_count += bool(pagina.get('responsive_valid', False))
                valid_aaaa_pages += bool(pagina.get('valid_aaa', False))  # Incrementa el contador si 'valid_aaa' es True
                #print(resultados_dominio)

            pages_title_long = sum(1 for pagina in resultados_dominio if pagina.get('title_long'))
            pages_title_short = sum(1 for pagina in resultados_dominio if pagina.get('title_short'))
            pages_title_dup = sum(1 for pagina in resultados_dominio if pagina.get('title_duplicate'))
            pages_desc_long = sum(1 for pagina in resultados_dominio if pagina.get('desc_long'))
            pages_desc_short = sum(1 for pagina in resultados_dominio if pagina.get('desc_short'))
            pages_h1_dup = sum(1 for pagina in resultados_dominio if pagina.get('h1_duplicate'))
            pages_img_1mb = sum(1 for pagina in resultados_dominio if pagina.get('images_1MB'))

            # Convert Counter to dictionary before writing to CSV
            idiomas_encontrados_dict = dict(idiomas_encontrados)

            # Imprimir para depuraciÃ³n
            logging.info(f'Dominio: {dominio}, Idiomas Encontrados: {idiomas_encontrados_dict}, Total 404: {total_404},Total enlaces inseguros: {total_enlaces_inseguros}, Paginas Inseguras: {paginas_inseguras}')
            print(f'Dominio: {dominio}, Idiomas Encontrados: {idiomas_encontrados_dict}')
            print(f'Total 404: {total_404}, Total enlaces inseguros: {total_enlaces_inseguros}, Paginas Inseguras: {paginas_inseguras}')
            print(f'Total Paginas con errores: {pages_err_orto}, Total paginas con alt vacios: {pages_alt_vacias}, Paginas Inseguras: {paginas_inseguras}')


            escritor_csv.writerow([dominio, total_paginas, duracion_total,
                                   codigos_respuesta, datos['hora_inicio'], datos['hora_fin'], datos['fecha'],
                                   html_valid_count, content_valid_count, responsive_valid_count, valid_aaaa_pages,
                                   idiomas_encontrados_dict, paginas_inseguras, total_404, total_enlaces_inseguros,
                                   pages_title_long, pages_title_short, pages_title_dup, pages_desc_long,
                                   pages_desc_short, pages_h1_dup, pages_img_1mb, id_escaneo,tiempo_medio, pages_err_orto, 
                                   pages_alt_vacias,peso_total_paginas, pdf_count, html_count, others_count])  # Actualizado con nuevos campos


def guardar_en_csv_y_json(resultados, nombre_archivo_base, modo='w'):
    campos = ['fecha_escaneo', 'dominio', 'codigo_respuesta', 'tiempo_respuesta', 'pagina', 'parent_url',
              'meta_tags', 'heading_tags', 'imagenes', 'enlaces_totales', 'enlaces_inseguros',
              'tipos_archivos', 'errores_ortograficos', 'num_errores_ortograficos', 'num_redirecciones',
              'alt_vacias', 'num_palabras', 'e_title', 'e_head', 'e_body', 'e_html', 'e_robots',
              'e_description', 'e_keywords', 'e_viewport', 'e_charset', 'html_valid', 'content_valid', 'responsive_valid',
              'image_types', 'wcagaaa', 'valid_aaa', 'lang', 'title_long', 'title_short', 'title_duplicate', 'desc_long', 
              'desc_short', 'h1_duplicate', 'images_1MB','id_escaneo','alt_vacias','peso_total_pagina','is_pdf']

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"{timestamp}-{nombre_archivo_base}"


    # Archivo CSV
    with open(f"results/{nombre_archivo}.csv", modo, newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
        if modo == 'w':
            escritor_csv.writeheader()

        for resultado in resultados:
            # AsegÃºrate de que las claves que no estÃ©n presentes en el diccionario tengan un valor por defecto de False
            resultado.setdefault('meta_tags', False)
            resultado.setdefault('heading_tags', False)
            resultado.setdefault('imagenes', False)
            resultado.setdefault('enlaces_totales', 0)
            resultado.setdefault('enlaces_inseguros', 0)
            resultado.setdefault('tipos_archivos', False)
            resultado.setdefault('errores_ortograficos', False)
            resultado.setdefault('num_errores_ortograficos', 0)
            resultado.setdefault('num_redirecciones', '0')
            resultado.setdefault('alt_vacias', 0)
            resultado.setdefault('num_palabras', 0)
            resultado.setdefault('e_title', False)
            resultado.setdefault('e_head', False)
            resultado.setdefault('e_body', False)
            resultado.setdefault('e_html', False)
            resultado.setdefault('e_robots', False)
            resultado.setdefault('e_description', False)
            resultado.setdefault('e_keywords', False)
            resultado.setdefault('e_viewport', False)
            resultado.setdefault('e_charset', False)
            resultado.setdefault('html_valid', 0)
            resultado.setdefault('content_valid', 0)
            resultado.setdefault('responsive_valid', 0)
            resultado.setdefault('wcagaaa', {})
            resultado.setdefault('image_types', {})  # AsegÃºrate de que 'image_types' estÃ© presente con un valor por defecto
            resultado.setdefault('lang', False)
            resultado.setdefault('images_1MB', 0)
            resultado.setdefault('is_pdf',-1)
            resultado.setdefault('valid_aaa', False)         

            # Reemplaza los valores None por False
            resultado = {k: False if v is None else v for k, v in resultado.items()}
            


            escritor_csv.writerow(resultado)

    # Archivo JSON
    #with open(f"results/{nombre_archivo}.json", modo, encoding='utf-8') as archivo_json:
    #    if modo == 'w':
    #        json.dump(resultados, archivo_json, ensure_ascii=False, indent=4)



if __name__ == "__main__":

    log_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_nombre_archivo = f"logs/{log_timestamp}-registro.log"
    
    # ConfiguraciÃ³n del sistema de registro
    logging.basicConfig(filename=log_nombre_archivo, level=logging.DEBUG)

    start_script_time = time.time()

    urls_a_escanear = ["http://zonnox.net","https://mc-mutuadeb.zonnox.net","http://hispalis.net","http://circuitosaljarafe.com"] #,"https://4glsp.com"]
    #urls_a_escanear += ["https://4glsp.com"] #,"https://santomera.es"]
    #urls_a_escanear = ["https://www.mc-mutual.com","https://mejoratuabsentismo.mc-mutual.com"] #,"https://prevencion.mc-mutual.com"]
    #urls_a_escanear += ["https://prevencion.mc-mutual.com"]
    patrones_exclusion = [] #'#','redirect'] #,'tel:'] #,"/asset_publisher/","/documents/", "/estaticos/", "productos","tel:"] #,"/asset_publisher/"
            # Agrega tus patrones para el modo rÃƒÂ¡pido
        #]

    extensiones_excluidas = [".apk", ".mp4",".avi",".msi",".zip",".7z",".rar",".mpeg",".zip/",".mp3"]  # Add the file extensions you want to exclude

    #engine = create_engine("mysql+mysqlconnector://usuario:contraseña@localhost/db?connect_timeout=300")

    # InicializaciÃ³n de la conexiÃ³n a la base de datos
    engine = create_engine('mysql+mysqlconnector://root:dldlt741@81.19.160.10/interec', pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600, echo=False)  # Cambia 'echo=True' a 'False' para desactivar el modo verbose
    Base.metadata.create_all(engine)

    # InicializaciÃ³n de la sesiÃ³n de SQLAlchemy
    Session = sessionmaker(bind=engine)

    with Session() as session:
        idiomas_por_dominio = {}
        resumen_escaneo = {}


        for url in urls_a_escanear:
            start_time = time.time()
            hora_inicio = datetime.now().strftime('%H:%M:%S')

            id_escaneo = secrets.token_hex(32)

            resultados_dominio = escanear_dominio(url, patrones_exclusion, extensiones_excluidas)
            end_time = time.time()

            duracion_total = end_time - start_time
            codigos_respuesta = [resultado['codigo_respuesta'] for resultado in resultados_dominio]
            total_paginas = len(resultados_dominio)


            # Verificar si la URL analizada es vÃ¡lida
            parsed_url = urlparse(url)
            if parsed_url.netloc:
                dominio = parsed_url.netloc
                # Crear un nuevo contador para cada dominio
                idiomas_encontrados = Counter()

                for pagina in resultados_dominio:
                    lang = pagina.get('lang')
                    if lang:
                        idiomas_encontrados[lang] += 1

                idiomas_por_dominio[dominio] = idiomas_encontrados.copy()

                print("idiomas por dominio")
                print(idiomas_por_dominio)

                print("idiomas encontrados")
                print(idiomas_encontrados)

                resumen_escaneo[dominio] = {
                    'dominio': dominio,
                    'total_paginas': total_paginas,
                    'duracion_total': duracion_total,
                    'codigos_respuesta': dict(zip(codigos_respuesta, [codigos_respuesta.count(c) for c in codigos_respuesta])),
                    'hora_inicio': hora_inicio,
                    'hora_fin': datetime.now().strftime('%H:%M:%S'),
                    'fecha': datetime.now().strftime('%Y-%m-%d'),
                    'html_valid_count': sum(1 for pagina in resultados_dominio if pagina.get('html_valid')),
                    'content_valid_count': sum(1 for pagina in resultados_dominio if pagina.get('content_valid')),
                    'responsive_valid_count': sum(1 for pagina in resultados_dominio if pagina.get('responsive_valid')),
                    'valid_aaaa_pages': sum(1 for pagina in resultados_dominio if pagina.get('valid_aaa')),
                    'idiomas': idiomas_encontrados,
                    'enlaces_inseguros': sum(1 for pagina in resultados_dominio if pagina.get('enlaces_inseguros')),
                    'paginas_inseguras': sum(1 for pagina in resultados_dominio if pagina.get('paginas_inseguras')),
                    'total_404': sum(1 for pagina in resultados_dominio if pagina.get('total_404')),
                    'pages_h1_dup': 0,  # Nuevo campo
                    'pages_img_1mb': 0,  # Nuevo campo
                    'id_escaneo': id_escaneo,
                    'tiempo_medio' : None,
                    'pages_err_orto' : 0, # sum(1 for pagina in resultados_dominio if pagina.get('num_errores_ortograficos') >= 1),
                    'pages_alt_vacias' : 0, #sum(1 for pagina in resultados_dominio if pagina.get('alt_vacias') >= 1)
                    'peso_total_paginas' : 0,
                    'pdf_count' : -1,
                    'html_count' :-1,
                    'others_count' :-1

                }

                guardar_en_csv_y_json(resultados_dominio, f"{dominio}_resultados")

                with Session() as session:
                    for resultado_pagina in resultados_dominio:
                        if 'pagina' in resultado_pagina and isinstance(resultado_pagina['pagina'], str):
                            resultado_pagina['pagina'] = resultado_pagina['pagina'].encode('utf-8')
                            resultado_pagina['id_escaneo'] = id_escaneo
                            resultado = Resultado(**resultado_pagina)
                            guardar_en_resultados(session, resultado)
                        else:
                            print(f"La URL {url} no se pudo analizar correctamente.")

        with Session() as session:
            for url, resumen in resumen_escaneo.items():
                sumario = Sumario(**resumen)
                sumario.idiomas = str(dict(idiomas_por_dominio[url]))
                guardar_en_sumario(session, sumario)

        with Session() as session:
            for dominio, resumen in resumen_escaneo.items():
                # Obtener la fecha más reciente para el dominio
                most_recent_date = session.query(func.max(Resultado.fecha_escaneo)).filter(
                    Resultado.dominio == dominio
                ).scalar()
                
                most_recent_id_escaneo = resumen['id_escaneo']

                # Si no hay registros para el dominio, continuar con el siguiente
                if most_recent_date is None:
                    continue
                
                # Seleccionar los registros de la tabla que cumplen las condiciones
                resultados_404 = session.query(Resultado).filter(
                    Resultado.dominio == dominio,
                    Resultado.codigo_respuesta == 404,
                    Resultado.id_escaneo == most_recent_id_escaneo
                    #Resultado.fecha_escaneo == most_recent_date
                ).all()

                # Obtener el número total de registros resultantes de esa consulta
                total_404 = len(resultados_404)

                # Imprimir el número total y los IDs de escaneo
                print(f"Total de registros 404 para el dominio {dominio}: {total_404}")
                
                # Seleccionar los registros de la tabla que cumplen las condiciones
                resultados_tiempo_respuesta = session.query(Resultado).filter(
                    Resultado.dominio == dominio,
                    Resultado.codigo_respuesta == 200,
                    ~func.locate('redirect=', Resultado.pagina),
                    Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
                    Resultado.id_escaneo == most_recent_id_escaneo
                ).all()

                print(f"Páginas con tiempo de respuesta para el dominio {dominio} en el último escaneo: {len(resultados_tiempo_respuesta)}")

                # Calcular el tiempo medio de respuesta
                tiempo_total = sum(resultado.tiempo_respuesta for resultado in resultados_tiempo_respuesta)
                tiempo_medio = tiempo_total / len(resultados_tiempo_respuesta) if len(resultados_tiempo_respuesta) > 0 else 0
                    
                 # Seleccionar los registros de la tabla que cumplen las condiciones
                resultados_pdf = session.query(Resultado).filter(
                    Resultado.dominio == dominio,
                    Resultado.is_pdf == 1,
                    Resultado.id_escaneo == most_recent_id_escaneo
                    #Resultado.fecha_escaneo == most_recent_date
                ).all() 
                
                pdf_count = len(resultados_pdf)

                 # Seleccionar los registros de la tabla que cumplen las condiciones
                resultados_html = session.query(Resultado).filter(
                    Resultado.dominio == dominio,
                    Resultado.is_pdf == 2,
                    Resultado.id_escaneo == most_recent_id_escaneo
                    #Resultado.fecha_escaneo == most_recent_date
                ).all() 

                html_count = len(resultados_html)
                
                # Seleccionar los registros de la tabla que cumplen las condiciones
                resultados_others = session.query(Resultado).filter(
                    Resultado.dominio == dominio,
                    Resultado.is_pdf == 0,
                    Resultado.id_escaneo == most_recent_id_escaneo
                    #Resultado.fecha_escaneo == most_recent_date
                ).all() 

                others_count = len(resultados_others)
                            
                # Obtener el id_escaneo más reciente para el dominio
                most_recent_id_escaneo = resumen['id_escaneo']

                # Si no hay registros en el sumario para el dominio, continuar con el siguiente
                if most_recent_id_escaneo is not None:
                    # Seleccionar los registros de la tabla que cumplen las condiciones
                    resultados_errores_ortograficos = session.query(Resultado).filter(
                        Resultado.dominio == dominio,
                        Resultado.codigo_respuesta == 200,
                        ~func.locate('redirect=', Resultado.pagina),
                        Resultado.num_errores_ortograficos > 0,
                        Resultado.id_escaneo == most_recent_id_escaneo
                    ).all()

                    print(f"Páginas con errores ortográficos para el dominio {dominio} en el último escaneo: {len(resultados_errores_ortograficos)}")
               
                    # Procesar los resultados
                    for resultado in resultados_errores_ortograficos:
                        # Descargar la página
                        print(f"Descargando la página: {resultado.pagina}")
                        #response = False 
                        response = requests.get(resultado.pagina)
                        if response.status_code == 200:
                            # Parsear el HTML y buscar palabras de errores ortográficos
                            soup = BeautifulSoup(response.text, 'html.parser')
                            for palabra in resultado.errores_ortograficos:
                                # Modificar el HTML
                                for tag in soup.find_all(string=palabra):
                                    new_tag = soup.new_tag('span', style='color:white;background-color:red')
                                    tag.wrap(new_tag)

                            # Guardar el HTML modificado en el campo html_copy
                            tmp = str(soup).encode('utf-8')
                            # Calcular la mitad del contenido
                            half_length = len(tmp) // 2
                            # Dividir el contenido en dos partes
                            resultado.html_copy = tmp[:half_length]
                            resultado.html_copy_dos = tmp[half_length:]

                            # Confirmar los cambios en la base de datos
                            # session.commit()
                else:
                    print(f"No hay registros en el sumario para el dominio {dominio}.")
                    
                # Obtener el objeto Sumario existente desde la base de datos
                sumario_existente = session.query(Sumario).filter_by(id_escaneo=resumen['id_escaneo']).first()

                # Verificar si se encontró un Sumario existente
                if sumario_existente:
                    # Actualizar los campos necesarios
                    sumario_existente.total_404 = total_404
                    sumario_existente.tiempo_medio = tiempo_medio  # Nueva columna "tiempo_medio"
                    sumario_existente.pdf_count = pdf_count
                    sumario_existente.html_count = html_count
                    sumario_existente.others_count = others_count
                    sumario_existente.pages_err_orto = len(resultados_errores_ortograficos)
                else:
                    # Manejar el caso en que no se encontró el Sumario existente (puede imprimir un mensaje o lanzar una excepción según tus necesidades)
                    print(f"¡No se encontró un Sumario existente para el id_escaneo {resumen['id_escaneo']}!")
            
                # Confirmar los cambios en la base de datos
                session.commit()

           

    end_script_time = time.time()
    script_duration = end_script_time - start_script_time

    logging.info(f'\nDuraciÃ³n total del script: {script_duration} segundos ({script_duration // 3600} horas y {(script_duration % 3600) // 60} minutos)')


    print(f'\nDuraciÃ³n total del script: {script_duration} segundos ({script_duration // 3600} horas y {(script_duration % 3600) // 60} minutos)')

    generar_informe_resumen(resumen_escaneo, 'resumen_escaneo.csv')
