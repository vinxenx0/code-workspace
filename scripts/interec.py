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
from lxml import etree
from spellchecker import SpellChecker

def extraer_texto_visible(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    visible_text = ' '.join(soup.stripped_strings)
    return visible_text


def analizar_ortografia(texto, idiomas=['es', 'fr', 'en']):
    spell = SpellChecker(language=idiomas, distance=1)

    # Eliminar números y símbolos de moneda
    translator = str.maketrans('', '', string.digits + string.punctuation)
    texto_limpio = texto.translate(translator)

    palabras = [palabra for palabra in texto_limpio.split() if len(palabra) > 3]
    errores_ortograficos = spell.unknown(palabras)
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
    return heading_tags_count

def extraer_informacion_imagenes(response_text, base_url):
    soup = BeautifulSoup(response_text, 'html.parser')
    img_tags = soup.find_all('img')
    info_imagenes = []

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

            info_imagen = {
                'filename': filename,
                'size_mb': size_mb,
                'url': src_url,
                'alt_text': alt,
                'broken': is_broken
            }

            info_imagenes.append(info_imagen)
        except Exception as e:
            print(f"Error al obtener información de la imagen {src_url}: {str(e)}")

    return info_imagenes


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
                'num_redirecciones': contar_redirecciones(url_actual)
            }

            if codigo_respuesta == 200 and response.headers['content-type'].startswith('text/html'):
                if es_html_valido(response.text):
                              
                    meta_tags_info = extraer_meta_tags(response.text) or {}
                    resultados_pagina['meta_tags'] = meta_tags_info

                    heading_tags_count = analizar_heading_tags(response.text)
                    resultados_pagina['heading_tags'] = heading_tags_count or {}

                    info_imagenes = extraer_informacion_imagenes(response.text, url_actual)
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


def guardar_en_csv(resultados, nombre_archivo, modo='w'):
    campos = ['fecha_escaneo', 'dominio', 'codigo_respuesta', 'tiempo_respuesta', 'pagina', 'parent_url',
              'meta_tags', 'heading_tags', 'imagenes', 'enlaces_totales', 'enlaces_inseguros',
              'tipos_archivos', 'errores_ortograficos', 'num_errores_ortograficos', 'num_redirecciones',
              'alt_vacias', 'num_palabras', 'e_title', 'e_head', 'e_body', 'e_html', 'e_robots',
              'e_description', 'e_keywords', 'e_viewport', 'e_charset', 'html_valid', 'content_valid', 'responsive_valid']
    
    with open(nombre_archivo, modo, newline='', encoding='utf-8') as archivo_csv:
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
            resultado.setdefault('num_redirecciones', False)
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

            # Reemplaza los valores None por False
            resultado = {k: False if v is None else v for k, v in resultado.items()}

            escritor_csv.writerow(resultado)


def generar_informe_resumen(resumen, nombre_archivo):
    header_present = os.path.exists(nombre_archivo)

    with open(nombre_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)

        if not header_present:
            escritor_csv.writerow(['dominio', 'total_paginas', 'duracion_total',
                                   'codigos_respuesta', 'hora_inicio', 'hora_fin', 'fecha',
                                   'html_valid_count', 'content_valid_count', 'responsive_valid_count'])

        for dominio, datos in resumen.items():
            codigos_respuesta = datos['codigos_respuesta']
            total_paginas = datos['total_paginas']
            duracion_total = datos['duracion_total']

            # Sigue sin contarlos
            html_valid_count = 0
            content_valid_count = 0
            responsive_valid_count = 0

            for pagina in datos.get('paginas', []):
                html_valid_count += bool(pagina.get('html_valid', False))
                content_valid_count += bool(pagina.get('content_valid', False))
                responsive_valid_count += bool(pagina.get('responsive_valid', False))

            escritor_csv.writerow([dominio, total_paginas, duracion_total,
                                   codigos_respuesta, datos['hora_inicio'], datos['hora_fin'], datos['fecha'],
                                   html_valid_count, content_valid_count, responsive_valid_count])



if __name__ == "__main__":
    start_script_time = time.time()
    urls_a_escanear = ["http://zonnox.net"] #,"http://circuitosaljarafe.com"]
    #urls_a_escanear = ["https://4glsp.com"]
    patrones_exclusion = ["redirect","#"]
    extensiones_excluidas = [".apk", ".mp4",".avi",".msi",".pdf"]  # Add the file extensions you want to exclude

    resumen_escaneo = {}

    for url in urls_a_escanear:
        start_time = time.time()
        hora_inicio = datetime.now().strftime('%H:%M:%S')
        resultados_dominio = escanear_dominio(url, patrones_exclusion, extensiones_excluidas)
        end_time = time.time()

        duracion_total = end_time - start_time
        codigos_respuesta = [resultado['codigo_respuesta'] for resultado in resultados_dominio]
        total_paginas = len(resultados_dominio)

        resumen_escaneo[urlparse(url).netloc] = {
            'total_paginas': total_paginas,
            'duracion_total': duracion_total,
            'codigos_respuesta': dict(zip(codigos_respuesta, [codigos_respuesta.count(c) for c in codigos_respuesta])),
            'hora_inicio': hora_inicio,
            'hora_fin': datetime.now().strftime('%H:%M:%S'),
            'fecha': datetime.now().strftime('%Y-%m-%d')
        }

        guardar_en_csv(resultados_dominio, f"{urlparse(url).netloc}_resultados.csv")

    end_script_time = time.time()
    script_duration = end_script_time - start_script_time

    print(f'\nDuración total del script: {script_duration} segundos ({script_duration // 3600} horas y {(script_duration % 3600) // 60} minutos)')

    generar_informe_resumen(resumen_escaneo, 'resumen_escaneo.csv')
