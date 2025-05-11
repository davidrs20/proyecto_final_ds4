from flask import Flask, render_template, request
import json

app = Flask(__name__, template_folder="sitio_web")

with open("datos/json/revistas_scimagojr.json", "r", encoding="utf-8") as f:
    revistas = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", revistas=revistas)

@app.route("/area")
def area():
    areas = set()
    for info in revistas.values():
        categorias = info.get("subject_area_category", "")
        if categorias:
            for parte in categorias.split(","):
                area = parte.strip()
                if area and not area.isdigit() and "Q" not in area:
                    areas.add(area)
    return render_template("area.html", areas=sorted(areas))

@app.route("/area/<nombre_area>")
def area_detalle(nombre_area):
    resultados = {}
    for nombre, info in revistas.items():
        categorias = info.get("subject_area_category", "")
        if categorias and nombre_area.lower() in categorias.lower():
            resultados[nombre] = info
    return render_template("area_detalle.html", area=nombre_area, resultados=resultados)

@app.route("/catalogos")
def catalogos():
    # Obtener todos los catálogos únicos (publisher) de las revistas
    catálogos = set(revista["publisher"] for revista in revistas.values() if revista.get("publisher"))
    
    return render_template("catalogos.html", catalogos=catálogos)

@app.route("/catalogo/<catalogo>")
def catalogo(catalogo):
    # Filtrar las revistas que pertenecen a este catálogo (publisher)
    revistas_en_catalogo = {nombre: info for nombre, info in revistas.items() if info.get("publisher") == catalogo}
    
    return render_template("revistas_en_catalogo.html", catalogo=catalogo, revistas=revistas_en_catalogo)

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

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip().lower()

    if q == "":  # Si no hay búsqueda, mostramos todas las revistas
        resultados = revistas
    else:
        resultados = {
            nombre: info for nombre, info in revistas.items()
            if q in nombre.lower()  # Compara el nombre de la revista
            or (info.get("publisher") and q in info["publisher"].lower())  # Verifica y compara el publisher
            or (info.get("subject_area_category") and q in info["subject_area_category"].lower())  # Verifica y compara el área temática
        }

    return render_template("resultados.html", resultados=resultados, query=q)


@app.route("/revista/<nombre_revista>")
def revista_detalle(nombre_revista):
    info = revistas.get(nombre_revista)
    if not info:
        return "Revista no encontrada", 404
    return render_template("revista_detalle.html", nombre=nombre_revista, info=info)

@app.route("/creditos")
def creditos():
    return render_template("creditos.html")

if __name__ == "__main__":
    app.run(debug=True)
