from flask import Flask, render_template, request
import json
import unicodedata



app = Flask(__name__, template_folder="sitio_web")

# Carga los datos desde el JSON
with open("datos/json/revistas_scimagojr.json", "r", encoding="utf-8") as f:
    revistas = json.load(f)
    print("Total revistas cargadas:", len(revistas))  # DEBUG


# Función para normalizar cadenas (quita acentos, convierte a minúsculas, elimina espacios extras)
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower().strip()

@app.route("/")
def index():
    return render_template("index.html", revistas=revistas)

@app.route("/area")
def area():
    # Creamos una lista de áreas sin importar si son None, vacías, etc.
    areas = set()

    for info in revistas.values():
        raw_area = info.get("subject_area_category")
        area = raw_area.strip() if isinstance(raw_area, str) else ""
        if not area:
            areas.add("Sin área")
        else:
            areas.add(area)

    areas = sorted(areas)
    return render_template("area.html", areas=areas)


@app.route("/area/<nombre_area>")
def ver_area(nombre_area):
    nombre_area_normalizado = normalizar(nombre_area)

    revistas_area = []
    for nombre, info in revistas.items():
        raw_area = info.get("subject_area_category")
        area = raw_area.strip() if isinstance(raw_area, str) else ""
        area_normalizada = normalizar(area) if area else normalizar("Sin área")
        
        if area_normalizada == nombre_area_normalizado:
            revistas_area.append({"nombre": nombre, **info})

    return render_template("revistas_por_area.html", area=nombre_area, revistas=revistas_area)


@app.route("/revista/<nombre_revista>")
def detalle_revista(nombre_revista):
    info = revistas.get(nombre_revista)
    if not info:
        return "Revista no encontrada", 404
    return render_template("detalle_revista.html", nombre=nombre_revista, info=info)

@app.route("/catalogos")
def catalogos():
    return render_template("catalogos.html", revistas=revistas)

@app.route("/explorar")
def explorar():
    area = request.args.get("area", "").lower()
    if area:
        revistas_filtradas = [
            {"nombre": nombre, **info} 
            for nombre, info in revistas.items() 
            if area in (info.get("subject_area_category") or "").lower()
        ]
    else:
        revistas_filtradas = [{"nombre": nombre, **info} for nombre, info in revistas.items()]
    
    return render_template("explorar.html", revistas=revistas_filtradas, area=area)

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").lower()
    resultados = {
        nombre: info for nombre, info in revistas.items()
        if q in nombre.lower()
    }
    return render_template("resultados.html", resultados=resultados, query=q)

@app.route("/creditos")
def creditos():
    return render_template("creditos.html")

if __name__ == "__main__":
    app.run(debug=True)
