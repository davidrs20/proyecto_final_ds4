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
    areas = {}
    for nombre, info in revistas.items():
        area = info.get("subject_area_category", "Sin área")
        if area not in areas:
            areas[area] = []
        areas[area].append((nombre, info))
    return render_template("area.html", areas=areas.keys())  


@app.route("/area/<nombre_area>")
def area_detalle(nombre_area):
    revistas_en_area = {
        nombre: info for nombre, info in revistas.items()
        if nombre_area in info.get("subject_area_category", "")
    }
    return render_template("area_detalle.html", area=nombre_area, revistas=revistas_en_area)

@app.route("/catalogos")
def catalogos():
    # Asumimos que "catalogo" se refiere a publisher o tipo
    return render_template("catalogos.html", revistas=revistas)

@app.route("/explorar")
def explorar():
    return render_template("explorar.html", revistas=revistas)

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
