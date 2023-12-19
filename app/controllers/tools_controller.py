# app/controllers/tools_controller.py

from flask import render_template
from flask_login import login_required
from app import app
from app.models.broken_links_results import Broken_Links_Results

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

@app.route('/seo/speed')
@login_required
def seo_speed():
    return render_template('tools/seo/seo_speed.html')

@app.route('/usabilidad/broken-links')
@login_required
def usa_broken_links():
    results = Broken_Links_Results.query.all()
    return render_template('tools/usa/usa_broken_links.html', results=results)

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

@app.route('/usabilidad/w3c')
@login_required
def usa_w3c():
    return render_template('tools/usa/usa_w3c.html')

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

