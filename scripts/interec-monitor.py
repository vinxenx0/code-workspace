# interec-monitor
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
import langid
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import LargeBinary



# Definir el modelo de la tabla "resultados"
Base = declarative_base()
class Resultado(Base):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_escaneo = Column(DateTime, default=datetime.now)
    dominio = Column(String(255))
    codigo_respuesta = Column(Integer)
    tiempo_respuesta = Column(Integer)
    pagina = Column(String(255))
    parent_url =  Column(String(255))
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

# Definir el modelo de la tabla "sumario"
class Sumario(Base):
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
    


# Función para guardar un resultado en la tabla "resultados"
def guardar_en_resultados(resultado):

    try:
        session = Session()
        session.add(resultado)
        session.commit()
    except IntegrityError as e:
        print(f"Error al guardar en 'resultados': {e}")
        session.rollback()
    finally:
        session.close()

# Función para guardar un sumario en la tabla "sumario"
def guardar_en_sumario(sumario):
    try:
        session = Session()
        session.add(sumario)
        session.commit()
    except IntegrityError as e:
        print(f"Error al guardar en 'sumario': {e}")
        session.rollback()
    finally:
        session.close()

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

    idioma_detectado = detectar_idioma(texto)
    if idioma_detectado and idioma_detectado in idiomas:
        try:
            speller = aspell.Speller('lang', idioma_detectado)

            # Eliminar números y símbolos de moneda, así como exclamaciones, interrogaciones y caracteres similares
            translator = str.maketrans('', '', string.digits + string.punctuation + '¡!¿?')
            texto_limpio = texto.translate(translator)

            palabras = [palabra for palabra in texto_limpio.split() if len(palabra) > 3]

            errores_ortograficos = [palabra for palabra in palabras if not speller.check(palabra)]
            
        except Exception as e:
            print(f"Error al procesar el idioma {idioma_detectado}: {e}")

    return errores_ortograficos

def extraer_meta_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_tags_info = [{'name': tag.get('name'), 'content': tag.get('content')} for tag in meta_tags]
    return meta_tags_info

def analizar_heading_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    heading_tags_count = {tag: len(soup.find_all(tag)) for tag in heading_tags}
    return heading_tags_count


def extraer_informacion_imagenes(response_text, base_url):
    soup = BeautifulSoup(response_text, 'html.parser')
    img_tags = soup.find_all('img')
    info_imagenes = []
    image_types = []

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
            print(f"Error al obtener información de la imagen {src_url}: {str(e)}")

    return info_imagenes, image_types

def contar_alt_vacias(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    img_tags = soup.find_all('img', alt='')

    return len(img_tags)

def contar_enlaces(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    enlaces = soup.find_all('a', href=True)
    enlaces_inseguros = [enlace['href'] for enlace in enlaces if enlace['href'].startswith('http://')]
    return len(enlaces), len(enlaces_inseguros)

# Sigue sin contarlos
def contar_tipos_archivos(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    archivos = soup.find_all(['a', 'img', 'video', 'audio', 'source'], href=True, src=True)
    tipos_archivos = {'pdf': 0, 'video': 0, 'sound': 0, 'image': 0, 'app': 0, 'others': 0}

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
        elif extension in ['apk', 'exe', 'msi']:
            tipos_archivos['app'] += 1
        else:
            tipos_archivos['others'] += 1

    return tipos_archivos

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
        return 'Redirección permanente (301)'
    elif status_code == 302:
        return 'Redirección temporal (302)'
    elif status_code == 303:
        return 'Redirección de otro recurso (303)'
    elif status_code == 307:
        return 'Redirección temporal (307)'
    elif status_code == 308:
        return 'Redirección permanente (308)'
    else:
        return 'Desconocido'
    
    
def contar_palabras_visibles(response_text):
    visible_text = extraer_texto_visible(response_text)
    palabras = visible_text.split()
    return len(palabras)


def analizar_meta_tags(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_tags_info = {
        'e_title': False,
        'e_head': False,
        'e_body': False,
        'e_html': False,
        'e_robots': False,
        'e_description': False,
        'e_keywords': False,
        'e_viewport': False,
        'e_charset': False
    }

    for tag in meta_tags:
        tag_name = tag.get('name', '').lower()
        tag_content = tag.get('content', '').lower()

        if tag_name in meta_tags_info:
            meta_tags_info[tag_name] = True
        elif tag_content in meta_tags_info:
            meta_tags_info[tag_content] = True

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

        # Imprime la salida estándar y la salida de error de pa11y
        #print("pa11y stdout:")
        #print(process.stdout)
        #print("pa11y stderr:")
        #print(process.stderr)

        # Verifica si el código de salida es diferente de cero (error)
        if process.returncode != 0:
            print(f"pa11y devolvió un código de salida no nulo {process.returncode}")
            return []  # Devuelve una lista vacía en caso de error

        # Obtiene la salida del comando pa11y (sin la primera línea que es la cabecera)
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
        return []  # Devuelve una lista vacía en caso de error



def escanear_dominio(url_dominio, exclusiones=[], extensiones_excluidas=[]):
    resultados = []
    dominio_base = urlparse(url_dominio).netloc
    urls_por_escanear = [(url_dominio, None)]
    urls_escaneadas = set()

    while urls_por_escanear:
        url_actual, parent_url = urls_por_escanear.pop()

        if url_actual in urls_escaneadas:
            continue

        try:
            print(f"Escanenado: {url_actual}")
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
                'num_redirecciones': 0 #contar_redirecciones(url_actual) 
            }

            if codigo_respuesta == 200 and response.headers['content-type'].startswith('text/html'):
                if es_html_valido(response.text):
                              
                    meta_tags_info = extraer_meta_tags(response.text) or {}
                    resultados_pagina['meta_tags'] = meta_tags_info

                    heading_tags_count = analizar_heading_tags(response.text)
                    resultados_pagina['heading_tags'] = heading_tags_count or {}

                    info_imagenes, image_types = extraer_informacion_imagenes(response.text, url_actual)
                    resultados_pagina['imagenes'] = info_imagenes or []
                    resultados_pagina['alt_vacias'] = contar_alt_vacias(response.text)
                    resultados_pagina['num_palabras'] = contar_palabras_visibles(response.text)

                    enlaces_totales, enlaces_inseguros = contar_enlaces(response.text)
                    resultados_pagina['enlaces_totales'] = enlaces_totales
                    resultados_pagina['enlaces_inseguros'] = enlaces_inseguros

                    tipos_archivos = contar_tipos_archivos(response.text)
                    resultados_pagina['tipos_archivos'] = tipos_archivos

                    texto_visible = extraer_texto_visible(response.text)
                    errores_ortograficos = analizar_ortografia(texto_visible)
                    resultados_pagina['errores_ortograficos'] = errores_ortograficos
                    resultados_pagina['num_errores_ortograficos'] = len(errores_ortograficos)

                    resultados_pagina['lang'] = detectar_idioma(response.text)

                    # Nuevos campos de revisión
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


                    resultados_pagina['wcagaaa'] = {'pa11y_results': pa11y_results_csv}
                    resultados_pagina['valid_aaa'] = not pa11y_results_csv  # True si no hay recomendaciones, False en caso contrario

                    

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
  

    with open(nombre_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)

        if not header_present:
            escritor_csv.writerow(['dominio', 'total_paginas', 'duracion_total',
                                   'codigos_respuesta', 'hora_inicio', 'hora_fin', 'fecha',
                                   'html_valid_count', 'content_valid_count', 'responsive_valid_count', 'valid_aaaa_pages', 'idiomas'])  # Agregar 'valid_aaaa_pages' a la lista de encabezados

        for dominio, datos in resumen.items():
            codigos_respuesta = datos['codigos_respuesta']
            total_paginas = datos['total_paginas']
            duracion_total = datos['duracion_total']

            for pagina in resultados_dominio:
                lang = pagina.get('lang')
                if lang:
                    idiomas_encontrados[lang] += 1

            # Sigue sin contarlos
            html_valid_count = 0
            content_valid_count = 0
            responsive_valid_count = 0
            valid_aaaa_pages = 0  # Contador para páginas con 'valid_aaa' True

            for pagina in datos.get('paginas', []):
                html_valid_count += bool(pagina.get('html_valid', False))
                content_valid_count += bool(pagina.get('content_valid', False))
                responsive_valid_count += bool(pagina.get('responsive_valid', False))
                valid_aaaa_pages += bool(pagina.get('valid_aaa', False))  # Incrementa el contador si 'valid_aaa' es True

            # Convert Counter to dictionary before writing to CSV
            idiomas_encontrados_dict = dict(idiomas_encontrados)

            # Imprimir para depuración
            print(f'Dominio: {dominio}, Idiomas Encontrados: {idiomas_encontrados_dict}')

            escritor_csv.writerow([dominio, total_paginas, duracion_total,
                                   codigos_respuesta, datos['hora_inicio'], datos['hora_fin'], datos['fecha'],
                                   html_valid_count, content_valid_count, responsive_valid_count, valid_aaaa_pages,
                                   idiomas_encontrados_dict])

def guardar_en_csv_y_json(resultados, nombre_archivo_base, modo='w'):
    campos = ['fecha_escaneo', 'dominio', 'codigo_respuesta', 'tiempo_respuesta', 'pagina', 'parent_url',
          'meta_tags', 'heading_tags', 'imagenes', 'enlaces_totales', 'enlaces_inseguros',
          'tipos_archivos', 'errores_ortograficos', 'num_errores_ortograficos', 'num_redirecciones',
          'alt_vacias', 'num_palabras', 'e_title', 'e_head', 'e_body', 'e_html', 'e_robots',
          'e_description', 'e_keywords', 'e_viewport', 'e_charset', 'html_valid', 'content_valid', 'responsive_valid',
          'image_types', 'wcagaaa', 'valid_aaa','lang']  # Agrega 'valid_aaa' a la lista de campos



    # Archivo CSV
    with open(f"{nombre_archivo_base}.csv", modo, newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
        if modo == 'w':
            escritor_csv.writeheader()

        for resultado in resultados:
            # Asegúrate de que las claves que no estén presentes en el diccionario tengan un valor por defecto de False
            resultado.setdefault('meta_tags', False)
            resultado.setdefault('heading_tags', False)
            resultado.setdefault('imagenes', False)
            resultado.setdefault('enlaces_totales', False)
            resultado.setdefault('enlaces_inseguros', False)
            resultado.setdefault('tipos_archivos', False)
            resultado.setdefault('errores_ortograficos', False)
            resultado.setdefault('num_errores_ortograficos', False)
            resultado.setdefault('num_redirecciones', '0')
            resultado.setdefault('alt_vacias', False)
            resultado.setdefault('num_palabras', False)
            resultado.setdefault('e_title', False)
            resultado.setdefault('e_head', False)
            resultado.setdefault('e_body', False)
            resultado.setdefault('e_html', False)
            resultado.setdefault('e_robots', False)
            resultado.setdefault('e_description', False)
            resultado.setdefault('e_keywords', False)
            resultado.setdefault('e_viewport', False)
            resultado.setdefault('e_charset', False)
            resultado.setdefault('html_valid', False)
            resultado.setdefault('content_valid', False)
            resultado.setdefault('responsive_valid', False)
            resultado.setdefault('wcagaaa', {})
            resultado.setdefault('image_types', {})  # Asegúrate de que 'image_types' esté presente con un valor por defecto
            resultado.setdefault('lang', False)

            # Reemplaza los valores None por False
            resultado = {k: False if v is None else v for k, v in resultado.items()}

            # Agrega el campo 'valid_aaa' y asegúrate de que tenga un valor por defecto de False
            resultado.setdefault('valid_aaa', False)

            escritor_csv.writerow(resultado)

    # Archivo JSON
    with open(f"{nombre_archivo_base}.json", modo, encoding='utf-8') as archivo_json:
        if modo == 'w':
            json.dump(resultados, archivo_json, ensure_ascii=False, indent=4)


    # Archivo JSON
    with open(f"{nombre_archivo_base}.json", modo, encoding='utf-8') as archivo_json:
        if modo == 'w':
            json.dump(resultados, archivo_json, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    start_script_time = time.time()
       
    urls_a_escanear = ["http://zonnox.net", "https://mc-mutuadeb.zonnox.net"] #"https://mc-mutuadeb.zonnox.net"] # "http://circuitosaljarafe.com"]
    #urls_a_escanear = ["https://4glsp.com"] #,"https://santomera.es"]
    #urls_a_escanear = ["https://www.mc-mutual.com","htps://mejoratuabsentismo.mc-mutual.com","https://prevencion.mc-mutual.com"]
    patrones_exclusion = ["redirect", "#","/asset_publisher/","/documents/", "/estaticos/", "productos"] #,"/asset_publisher/"
            # Agrega tus patrones para el modo rÃ¡pido
        #]

    extensiones_excluidas = [".apk", ".mp4",".avi",".msi",".pdf"]  # Add the file extensions you want to exclude
    
    # Inicialización de la conexión a la base de datos
    engine = create_engine('mysql+mysqlconnector://', echo=False)  # Cambia 'echo=True' a 'False' para desactivar el modo verbose
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    idiomas_por_dominio = {}
    resumen_escaneo = {}

    for url in urls_a_escanear:
        start_time = time.time()
        hora_inicio = datetime.now().strftime('%H:%M:%S')
        resultados_dominio = escanear_dominio(url, patrones_exclusion, extensiones_excluidas)
        end_time = time.time()

        duracion_total = end_time - start_time
        codigos_respuesta = [resultado['codigo_respuesta'] for resultado in resultados_dominio]
        total_paginas = len(resultados_dominio)


        # Verificar si la URL analizada es válida
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
                'idiomas': idiomas_encontrados
            }

            guardar_en_csv_y_json(resultados_dominio, f"{dominio}_resultados")
            
            for resultado_pagina in resultados_dominio:
                # Verificar si 'pagina' es texto antes de intentar convertirlo a datos binarios
                if 'pagina' in resultado_pagina and isinstance(resultado_pagina['pagina'], str):
                    resultado_pagina['pagina'] = resultado_pagina['pagina'].encode('utf-8')

                resultado = Resultado(**resultado_pagina)
                guardar_en_resultados(resultado)

        else:
            print(f"La URL {url} no se pudo analizar correctamente.")

    for url, resumen in resumen_escaneo.items():
        sumario = Sumario(**resumen)
        # Utiliza el diccionario de idiomas específico de cada dominio
        sumario.idiomas = str(dict(idiomas_por_dominio[url]))
        # solo para local 
        guardar_en_sumario(sumario)

    end_script_time = time.time()
    script_duration = end_script_time - start_script_time

    print(f'\nDuración total del script: {script_duration} segundos ({script_duration // 3600} horas y {(script_duration % 3600) // 60} minutos)')

    generar_informe_resumen(resumen_escaneo, 'resumen_escaneo.csv')
    # solo para local 
    #guardar_en_sumario(sumario)
