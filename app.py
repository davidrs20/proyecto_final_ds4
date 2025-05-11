from flask import Flask, render_template, request, redirect, url_for, session
import json
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder="sitio_web")
app.secret_key = "clave_secreta_segura"  # Cambia esto por una clave segura

with open("datos/json/revistas_scimagojr.json", "r", encoding="utf-8") as f:
    revistas = json.load(f)

usuarios = {
    "admin": "1234",  # usuario: contraseña
    "usuario1": "abcd"
}

# Utilidad
def extraer_url_widget(widget_html):
    soup = BeautifulSoup(widget_html, "html.parser")
    a_tag = soup.find("a")
    return a_tag["href"] if a_tag else None

@app.route("/")
def index():
    return render_template("index.html", revistas=revistas)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        if usuario in usuarios and usuarios[usuario] == password:
            session["usuario"] = usuario
            session.setdefault("favoritos", {})  # Diccionario con claves por usuario
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("index"))

@app.route("/guardar/<nombre_revista>")
def guardar(nombre_revista):
    if "usuario" not in session:  # Verificar que el usuario esté autenticado
        return redirect(url_for("login"))
    
    user = session["usuario"]  # Obtener el nombre de usuario de la sesión
    
    # Asegurarse de que la clave 'favoritos' existe en la sesión
    if "favoritos" not in session:
        session["favoritos"] = {}
    
    # Obtener la lista de favoritos del usuario actual
    favoritos = session["favoritos"].get(user, [])
    
    # Si la revista no está en la lista de favoritos, agregarla
    if nombre_revista not in favoritos:
        favoritos.append(nombre_revista)
    
    # Guardar los favoritos del usuario nuevamente en la sesión
    session["favoritos"][user] = favoritos
    session.modified = True  # Asegurarse de que la sesión se guarda correctamente

    # Redirigir al detalle de la revista guardada
    return redirect(url_for("revista_detalle", nombre_revista=nombre_revista))


    user = session["usuario"]
    if "favoritos" not in session:
        session["favoritos"] = {}

    favoritos = session["favoritos"].get(user, [])
    if nombre_revista not in favoritos:
        favoritos.append(nombre_revista)
        session["favoritos"][user] = favoritos
    return redirect(url_for("revista_detalle", nombre_revista=nombre_revista))

@app.route("/mis_revistas")
def mis_revistas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    user = session["usuario"]
    favoritos = session.get("favoritos", {}).get(user, [])
    favoritas = {nombre: revistas[nombre] for nombre in favoritos if nombre in revistas}
    return render_template("mis_revistas.html", revistas=favoritas)

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
    catalogo_lista = sorted(set(revista["publisher"] for revista in revistas.values() if revista.get("publisher")))
    return render_template("catalogos.html", catalogos=catalogo_lista)

@app.route("/catalogo/<catalogo>")
def catalogo(catalogo):
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
    info['url'] = extraer_url_widget(info.get('widget', ''))
    return render_template("revista_detalle.html", nombre=nombre_revista, info=info)

@app.route("/creditos")
def creditos():
    return render_template("creditos.html")

if __name__ == "__main__":
    app.run(debug=True)
