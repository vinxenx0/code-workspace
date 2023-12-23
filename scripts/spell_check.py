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

def contar_enlaces(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    enlaces = soup.find_all('a', href=True)
    enlaces_inseguros = [enlace['href'] for enlace in enlaces if enlace['href'].startswith('http://')]
    return len(enlaces), len(enlaces_inseguros)

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

def contar_redirecciones(url, max_redirecciones=10):
    count = 0
    current_url = url

    while count < max_redirecciones:
        response = requests.head(current_url, allow_redirects=True)
        if response.status_code // 100 == 3:
            current_url = response.headers['Location']
            count += 1
        else:
            break

    return count

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
            num_redirecciones = contar_redirecciones(url_actual)
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
                'num_redirecciones': num_redirecciones
            }

            if codigo_respuesta == 200 and response.headers['content-type'].startswith('text/html'):
                if es_html_valido(response.text):
                    meta_tags_info = extraer_meta_tags(response.text)
                    resultados_pagina['meta_tags'] = meta_tags_info

                    heading_tags_count = analizar_heading_tags(response.text)
                    resultados_pagina['heading_tags'] = heading_tags_count

                    #info_imagenes = {}
                    info_imagenes = extraer_informacion_imagenes(response.text, url_actual)
                    resultados_pagina['imagenes'] = info_imagenes
                    
                    enlaces_totales, enlaces_inseguros = contar_enlaces(response.text)
                    resultados_pagina['enlaces_totales'] = enlaces_totales
                    resultados_pagina['enlaces_inseguros'] = enlaces_inseguros

                    #tipos_archivos = {} # Se omite la revisión de tipos de archivos si no es HTML válido
                    tipos_archivos = contar_tipos_archivos(response.text)
                    resultados_pagina['tipos_archivos'] = tipos_archivos

                    texto_visible = extraer_texto_visible(response.text)
                    errores_ortograficos = analizar_ortografia(texto_visible)
                    resultados_pagina['errores_ortograficos'] = errores_ortograficos
                    resultados_pagina['num_errores_ortograficos'] = len(errores_ortograficos)

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
              'tipos_archivos', 'errores_ortograficos', 'num_errores_ortograficos', 'num_redirecciones']
    with open(nombre_archivo, modo, newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
        if modo == 'w':
            escritor_csv.writeheader()
        escritor_csv.writerows(resultados)


def generar_informe_resumen(resumen, nombre_archivo):
    header_present = os.path.exists(nombre_archivo)

    with open(nombre_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)

        if not header_present:
            escritor_csv.writerow(['dominio', 'total_paginas', 'duracion_total',
                                   'codigos_respuesta', 'hora_inicio', 'hora_fin', 'fecha'])

        for dominio, datos in resumen.items():
            codigos_respuesta = datos['codigos_respuesta']
            escritor_csv.writerow([dominio, datos['total_paginas'], datos['duracion_total'],
                                   codigos_respuesta, datos['hora_inicio'], datos['hora_fin'], datos['fecha']])

if __name__ == "__main__":
    start_script_time = time.time()
    urls_a_escanear = ["http://zonnox.net","http://circuitosaljarafe.com"]
    #urls_a_escanear = ["https://4glsp.com"]
    patrones_exclusion = ["redirect","#"]
    extensiones_excluidas = [".apk", ".mp4",".avi",".msi",".pdf",".doc",".zip"]  # Add the file extensions you want to exclude

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
