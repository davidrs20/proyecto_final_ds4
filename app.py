from flask import Flask, render_template, request
import json
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder="sitio_web")

with open("datos/json/revistas_scimagojr.json", "r", encoding="utf-8") as f:
    revistas = json.load(f)

def extraer_url_widget(widget_html):
    soup = BeautifulSoup(widget_html, "html.parser")
    a_tag = soup.find("a")
    return a_tag["href"] if a_tag else None

@app.route("/")
def index():
    return render_template("index.html", revistas=revistas)

@app.route("/area")
def area():
    areas = set()
    for info in revistas.values():
        categorias = info.get("subjet_area_and_category", {})
        if isinstance(categorias, dict):
            for area_general, subcategorias in categorias.items():
                if area_general and not area_general.isdigit() and "Q" not in area_general:
                    areas.add(area_general.strip())
                if isinstance(subcategorias, list):
                    for sub in subcategorias:
                        if sub and not sub.isdigit() and "Q" not in sub:
                            areas.add(sub.strip())
    return render_template("area.html", areas=sorted(areas))

@app.route("/area/<nombre_area>")
def area_detalle(nombre_area):
    resultados = {}
    for nombre, info in revistas.items():
        categorias = info.get("subjet_area_and_category", {})
        if isinstance(categorias, dict):
            for area_general, subcategorias in categorias.items():
                if nombre_area.lower() in area_general.lower():
                    resultados[nombre] = info
                    break
                if isinstance(subcategorias, list):
                    for sub in subcategorias:
                        if nombre_area.lower() in sub.lower():
                            resultados[nombre] = info
                            break
    return render_template("area_detalle.html", area=nombre_area, revistas=resultados)

@app.route("/catalogos")
def mostrar_catalogos(): 
    # Obtener todos los catálogos únicos (publisher) de las revistas
    catalogo_lista = sorted(set(revista["publisher"] for revista in revistas.values() if revista.get("publisher")))
    return render_template("catalogos.html", catalogos=catalogo_lista)

@app.route("/catalogo/<catalogo>")
def catalogo(catalogo):
    # Filtrar las revistas que pertenecen a este catálogo (publisher)
    revistas_en_catalogo = {nombre: info for nombre, info in revistas.items() if info.get("publisher") == catalogo}
    return render_template("revistas_en_catalogo.html", catalogo=catalogo, revistas=revistas_en_catalogo)

@app.route('/buscar_catalogo')
def buscar_catalogo():
    query = request.args.get('q', '').lower()
    catalogo_lista = sorted(set(revista["publisher"] for revista in revistas.values() if revista.get("publisher")))
    resultados = [c for c in catalogo_lista if query in c.lower()]
    return render_template('catalogos.html', catalogos=resultados)


@app.route("/explorar")
@app.route("/explorar/<letra>")
def explorar(letra=None):
    if letra:
        revistas_filtradas = {
            nombre: info for nombre, info in revistas.items()
            if nombre.lower().startswith(letra.lower())
        }
    else:
        revistas_filtradas = {}
    return render_template("explorar.html", letras='abcdefghijklmnopqrstuvwxyz', revistas=revistas_filtradas, letra=letra)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').lower()  # Obtiene la consulta de búsqueda
    resultados = {nombre: info for nombre, info in revistas.items() if query in nombre.lower()}
    return render_template('resultados.html', query=query, resultados=resultados)

@app.route("/revista/<nombre_revista>")
def revista_detalle(nombre_revista):
    info = revistas.get(nombre_revista)
    if not info:
        return "Revista no encontrada", 404
    info['url'] = extraer_url_widget(info.get('widget', ''))
    return render_template("revista_detalle.html", nombre=nombre_revista, info=info)

@app.route("/creditos")
def creditos():
    return render_template("creditos.html")

if __name__ == "__main__":
    app.run(debug=True)