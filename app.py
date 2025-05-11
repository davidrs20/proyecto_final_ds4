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
    # Agrupar por áreas
    areas = {}
    for nombre, info in revistas.items():
        area = info.get("subject_area_category", "Sin área")
        if area not in areas:
            areas[area] = []
        areas[area].append((nombre, info))
    return render_template("area.html", areas=areas)

if __name__ == "__main__":
    app.run(debug=True)
