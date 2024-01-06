# app/controllers/tools_controller.py

import json
from flask import render_template, jsonify
from flask_login import login_required
from app import app, db
from sqlalchemy import and_, desc,func, case, literal, literal_column, text
from app.models.database import Resultado, Sumario
from config import IDS_ESCANEO
from sqlalchemy.orm import class_mapper

# Implementación del filtro fromjson
def fromjson(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

# Agregar el filtro a la aplicación Flask
app.jinja_env.filters['fromjson'] = fromjson

ids_escaneo_especificos = IDS_ESCANEO

# Tools rutas

@app.route('/informes/consultas')
@login_required
def consultas():
    return render_template('tools/informes.html')

@app.route('/informes/mejoras')
@login_required
def mejoras():
    return render_template('tools/performance.html')

@app.route('/seo/health')
@login_required
def seo_health_check():
    return render_template('tools/seo/seo_health.html')

@app.route('/seo/posicionamiento')
@login_required
def seo_posicionamiento():
    return render_template('tools/seo/seo_posicionamiento.html')

@app.route('/seo/keywords')
@login_required
def seo_keywords():
    return render_template('tools/seo/seo_keywords.html')

@app.route('/seo/traffic')
@login_required
def seo_traffic():
    return render_template('tools/seo/seo_traffic.html')

@app.route('/seo/competencia')
@login_required
def seo_competencia():
    return render_template('tools/seo/seo_competencia.html')

@app.route('/seo/backlinks')
@login_required
def seo_backlinks():
    return render_template('tools/seo/seo_backlinks.html')

@app.route('/seo/indexing')
@login_required
def seo_indexing():
    return render_template('tools/seo/seo_indexing.html')

@app.route('/seo/resumen')
@login_required
def seo_resumen():
    
    dominios_especificos = ["zonnox.net", "mc-mutuadeb.zonnox.net"]
    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.dominio.in_(dominios_especificos))
        .all()
    )
    
     # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    return render_template('resumen.html', sumario=json.dumps(sumarios_dict), dominios=dominios_especificos)
  

@app.route('/velocidad')
@login_required
def velocidad():
    
      # IDs de escaneo específicos ids_escaneo_especificos = IDS_ESCANEO

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_velocidad = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio, Resultado.tiempo_respuesta, Resultado.pagina, Resultado.lang,
                        Resultado.imagenes, Resultado.images_1MB, Resultado.image_types, Resultado.id #is_pdf
                        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200,
            Resultado.tiempo_respuesta > 3,
            Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            Resultado.tiempo_respuesta != '',
            Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None) 
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )    
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all()
    )
    # Consulta para obtener la información de carga agrupada por segundos
    cargas_por_segundos = {}

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (Resultado.tiempo_respuesta < 1, 'Menos de 1 segundo'),
                ((Resultado.tiempo_respuesta >= 1) & (Resultado.tiempo_respuesta <= 3), '1 a 3 segundos'),
                ((Resultado.tiempo_respuesta > 3) & (Resultado.tiempo_respuesta <= 7), '3 a 7 segundos'),
                ((Resultado.tiempo_respuesta > 7) & (Resultado.tiempo_respuesta <= 15), '7 a 15 segundos'),
                ((Resultado.tiempo_respuesta > 15) & (Resultado.tiempo_respuesta <= 30), '15 a 30 segundos'),
                ((Resultado.tiempo_respuesta > 30) & (Resultado.tiempo_respuesta <= 60), '30 a 60 segundos'),
                ((Resultado.tiempo_respuesta > 60) & (Resultado.tiempo_respuesta <= 90), '60 a 90 segundos'),
                (Resultado.tiempo_respuesta > 90, 'Más de 90 segundos')
            ).label('intervalo_carga'),
            func.count().label('count')
        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200

        ) 
            
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga', Resultado.dominio)
        .all()
    )

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in cargas_por_segundos:
            cargas_por_segundos[id_escaneo] = []

        cargas_por_segundos[id_escaneo].append((dominio, intervalo_carga, count))

    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.id_escaneo.in_(ids_escaneo_especificos))
        .all()
    )
    
     # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)


    # Enviamos los resultados al template
    return render_template('tools/seo/velocidad.html', resultados=paginas_velocidad, detalles=cargas_por_segundos, graficos=json.dumps(cargas_por_segundos), resumen=sumarios, sumario = json.dumps(sumarios_dict))





@app.route('/enlaces-rotos')
@login_required
def enlaces_rotos():
    # IDs de escaneo específicos
    #ids_escaneo_especificos = ['4b99956ba942f7986ccc2e5c992c3a2a111385bfdbbfa2223818c6a8d9e28510',\
    #    '41038960d6084d0e2ba5416c0c2a52777cc40e119b7c69fb0aeaa4b8231cd2e0',\
    #    '5b485f2d386e81e56d67e6f1663d7d965f69985e11d771e56b0caf6f5ecb0849'
          #  ]  # Reemplaza con los IDs específicos que se proporcionarán

    #ids_escaneo_especificos = IDS_ESCANEO
    
    # Consulta principal para obtener todas las URLs que coincidan con los IDs de escaneo proporcionados
    results = (
        db.session.query(Resultado)
        .filter(Resultado.codigo_respuesta == 404)
        .filter(Resultado.id_escaneo.in_(ids_escaneo_especificos))
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .all()
    )

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.id_escaneo.in_(ids_escaneo_especificos))
        .all()
    )

    # Envía los resultados al template
    return render_template('tools/usa/enlaces_rotos.html', resultados=results, resumen=sumarios, detalles = [])


@app.route('/usabilidad/broken-links')
@login_required
def usa_broken_links():
    return render_template('tools/usa/usa_broken_links.html')



@app.route('/usabilidad/font-colors')
@login_required
def usa_font_colors():
    return render_template('tools/usa/usa_font_colors.html')

@app.route('/usabilidad/form')
@login_required
def usa_form():
    return render_template('tools/usa/usa_form.html')

@app.route('/usabilidad/nav')
@login_required
def usa_nav():
    return render_template('tools/usa/usa_nav.html')

@app.route('/usabilidad/responsive')
@login_required
def usa_responsive():
    return render_template('tools/usa/usa_responsive.html')

@app.route('/responsive')
@login_required
def responsive():
    
       # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_responsive = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio, Resultado.pagina, Resultado.lang,
                        Resultado.e_viewport, Resultado.html_valid, Resultado.responsive_valid, Resultado.id,
                        Resultado.valid_aaa, Resultado.meta_tags #is_pdf
                        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200,
            Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.tiempo_respuesta != '',
            #Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None) 
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )    
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/documents/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all()
    )
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}


    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (
                    and_(Resultado.e_viewport != 1, Resultado.e_viewport.isnot(None)),
                    'Sin etiqueta viewport'
                ),
                (
                    and_(Resultado.html_valid != 1, Resultado.html_valid.isnot(None)),
                    'Sin estructura HTML valida'
                ),
                (
                    and_(Resultado.responsive_valid != 1, Resultado.responsive_valid.isnot(None)),
                    'No cumple con estándares '
                ),
                (
                    and_(Resultado.valid_aaa != 1, Resultado.valid_aaa.isnot(None)),
                    'No validan con WACG - AAA '
                ),
                else_='Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')
        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200
        )         
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga', Resultado.dominio)
        .all()
    )

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append((dominio, intervalo_carga, count))

    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.id_escaneo.in_(ids_escaneo_especificos))
        .all()
    )

    # Enviamos los resultados al template
    return render_template('tools/usa/responsive.html', resultados=paginas_responsive, detalles=resultados_agrupados, resumen=sumarios)


@app.route('/usabilidad/w3c')
@login_required
def usa_w3c():
    return render_template('tools/usa/usa_w3c.html')


@app.route('/analisis-aaa')
@login_required
def analisis_aaa():
   
    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_wcagaaa = (
            db.session.query(
            Resultado.fecha_escaneo, Resultado.dominio, Resultado.pagina, Resultado.lang,
            # Aplicar json.loads a la columna Resultado.wcagaaa
            literal_column("JSON_UNQUOTE(JSON_EXTRACT(resultados.wcagaaa, '$.pa11y_results'))").label('wcagaaa'),
            Resultado.html_valid, Resultado.responsive_valid, Resultado.id,
            Resultado.valid_aaa, Resultado.meta_tags #is_pdf
        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200,
            Resultado.valid_aaa == 0,
            #Resultado.wcagaaa.isnot(None),  # Seleccionar solo cuando wcagaaa no es None
            #Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []} 
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None) 
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )    
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/asset_publisher/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all()
    )
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}


    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (Resultado.valid_aaa == 1, 'Pasan AAA'),
                (Resultado.valid_aaa != 1, 'No pasan AAA'),
                else_='Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
                
            ).label('intervalo_carga'),
            func.count().label('count')
        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200
        )         
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga', Resultado.dominio)
        .all()
    )

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append((dominio, intervalo_carga, count))

    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.id_escaneo.in_(ids_escaneo_especificos))
        .all()
    )

    # Enviamos los resultados al template
    return render_template('tools/usa/analisis_aaa.html', resultados=paginas_wcagaaa, detalles=resultados_agrupados, resumen=sumarios)



@app.route('/accesibilidad/compatible')
@login_required
def acc_comp():
    return render_template('tools/acc/acc_comp.html')

@app.route('/accesibilidad/contraste')
@login_required
def acc_contraste():
    return render_template('tools/acc/acc_contraste.html')

@app.route('/accesibilidad/imagenes')
@login_required
def acc_images():
    return render_template('tools/acc/acc_images.html')

@app.route('/accesibilidad/lectores')
@login_required
def acc_lectores():
    return render_template('tools/acc/acc_lectores.html')

@app.route('/accesibilidad/media')
@login_required
def acc_media():
    return render_template('tools/acc/acc_media.html')

@app.route('/accesibilidad/sintax')
@login_required
def acc_sintax():
    return render_template('tools/acc/acc_sintax.html')

@app.route('/accesibilidad/structure')
@login_required
def acc_structure():
    return render_template('tools/acc/acc_structure.html')

@app.route('/accesibilidad/validators')
@login_required
def acc_validators():
    return render_template('tools/acc/acc_validators.html')


@app.route('/ortografia/<int:resultado_id>')
@login_required
def mostrar_html_copy(resultado_id):
    # Obtener el resultado de la base de datos según el resultado_id
    resultado = Resultado.query.get(resultado_id)

    # Verificar si el resultado existe
    if not resultado:
        # Puedes manejar esto según tus necesidades (por ejemplo, mostrar un error)
        return "Resultado no encontrado", 404

    # Renderizar la plantilla con el contenido de html_copy
    return render_template('tools/dicc/html_copy.html', contenido_html=resultado.html_copy)



@app.route('/ortografia')
@login_required
def ortografia():
    
          # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_ortografia = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio, Resultado.pagina, Resultado.lang,
                        Resultado.errores_ortograficos, Resultado.num_errores_ortograficos, 
                        Resultado.html_copy, Resultado.id, Resultado.meta_tags
                        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200,
            Resultado.num_errores_ortograficos >= 1,
            #Resultado.wcagaaa.isnot(None),  # Seleccionar solo cuando wcagaaa no es None
            #Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []} 
            Resultado.html_copy.isnot(None), #,  # Filtrar resultados con tiempo_respuesta False
            Resultado.errores_ortograficos != 'false'
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )    
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%?%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/asset_publisher/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all()
    )
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}


    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (Resultado.num_errores_ortograficos == 0, 'Sin errores'),
                (Resultado.num_errores_ortograficos > 0, 'Con errores'),
                else_='Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
                
            ).label('intervalo_carga'),
            func.count().label('count')
        )
        .filter(
            Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.codigo_respuesta == 200
        )         
        .filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga', Resultado.dominio)
        .all()
    )

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append((dominio, intervalo_carga, count))

    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        .filter(Sumario.id_escaneo.in_(ids_escaneo_especificos))
        .all()
    )

    # Enviamos los resultados al template
    return render_template('tools/dicc/ortografia.html', resultados=paginas_ortografia, detalles=resultados_agrupados, resumen=sumarios)


@app.route('/diccionarios/spanish')
@login_required
def dicc_spanish():
    return render_template('tools/dicc/dicc_spanish.html')

@app.route('/diccionarios/english')
@login_required
def dicc_english():
    return render_template('tools/dicc/dicc_english.html')

@app.route('/diccionarios/catalan')
@login_required
def dicc_catalan():
    return render_template('tools/dicc/dicc_catalan.html')


@app.route('/diagnosis/dominios')
@login_required
def diag_domains():
    return render_template('tools/diag/diag_domains.html')

@app.route('/diagnosis/spam')
@login_required
def diag_spam():
    return render_template('tools/diag/diag_spam.html')

@app.route('/diagnosis/copyright')
@login_required
def diag_copyright():
    return render_template('tools/diag/diag_copyright.html')

@app.route('/diagnosis/gdpr')
@login_required
def diag_gdpr():
    return render_template('tools/diag/diag_gdpr.html')

@app.route('/diagnosis/politicas-legales')
@login_required
def diag_textos_legales():
    return render_template('tools/diag/diag_textos_legales.html')

@app.route('/tools/config')
@login_required
def tools_config():
    return render_template('tools/config.html')

