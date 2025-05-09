import os
import csv
import json

# Rutas
base_path = "datos"
areas_path = os.path.join(base_path, "csv", "areas")
catalogos_path = os.path.join(base_path, "csv", "catalogos")
json_output_path = os.path.join(base_path, "json", "revistas.json")

# Diccionario final
revistas = {}

# Leer archivos de áreas
for archivo in os.listdir(areas_path):
    if archivo.endswith(".csv"):
        area = archivo[:-4].upper()
        with open(os.path.join(areas_path, archivo), 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            for fila in lector:
                if not fila: continue
                revista = fila[0].strip().lower()
                if revista not in revistas:
                    revistas[revista] = {"areas": [], "catalogos": []}
                if area not in revistas[revista]["areas"]:
                    revistas[revista]["areas"].append(area)

# Leer archivos de catálogos
for archivo in os.listdir(catalogos_path):
    if archivo.endswith(".csv"):
        catalogo = archivo[:-4].upper()
        with open(os.path.join(catalogos_path, archivo), 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            for fila in lector:
                if not fila: continue
                revista = fila[0].strip().lower()
                if revista not in revistas:
                    revistas[revista] = {"areas": [], "catalogos": []}
                if catalogo not in revistas[revista]["catalogos"]:
                    revistas[revista]["catalogos"].append(catalogo)




