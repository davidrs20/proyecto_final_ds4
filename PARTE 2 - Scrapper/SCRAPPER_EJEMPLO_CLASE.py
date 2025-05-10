'''
Scrapper para scimago
'''

import os
import json
import time
import requests
from bs4 import BeautifulSoup

# Entrada json, archivo de la parte 1
ENTRADA_JSON = 'datos/json/revistas.json'

# Aqui se guarda la informacion obtenia del scrapper
SALIDA_JSON = 'datos/json/revistas_info.json'

# Carga el diccionario de revistas desde el archivo json original
def cargar_revistas(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

# Carga los datos ya guardados, para no repetir el scraping
def cargar_datos_existentes(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Guarda los resultados del scraping en un archivo json
def guardar_resultados(datos, archivo_salida):
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

# Construye la URL de búsqueda en scimago para una revista
def construir_url(nombre_revista):
    return f'https://www.scimagojr.com/journalsearch.php?q={nombre_revista.replace(" ", "+")}'

def obtener_url_revista(nombre_revista):
    url = construir_url(nombre_revista)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Selector actualizado: busca dentro de .search_results
    enlace = soup.select_one(".search_results a[href*='journals/']")
    if enlace:
        return 'https://www.scimagojr.com/' + enlace['href']
    return None


def get_texto(soup, selector):
    el = soup.select_one(selector)
    return el.text.strip() if el else None

# Realiza el scraping de los datos desde la página específica de una revista
def extraer_info_revista(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Se extraen los campos requeridos usando selectores CSS
    info = {
        'sitio_web': get_texto(soup, "a[title='Homepage']"),
        'h_index': get_texto(soup, "p.hindexnumber"),
        'subject_area': get_texto(soup, "div:has(h2:contains('Subject Area and Category')) p"),
        'publisher': get_texto(soup, "div:has(h2:contains('Publisher')) p"),
        'issn': get_texto(soup, "div:has(h2:contains('ISSN')) p"),
        'widget': get_texto(soup, "textarea#sjr_widget"),
        'tipo_publicacion': get_texto(soup, "div:has(h2:contains('Publication type')) p"),
        'ultima_visita': time.strftime("%Y-%m-%d")  
    }

    return info

# Función principal
def main():
    revistas = cargar_revistas(ENTRADA_JSON)
    resultados = cargar_datos_existentes(SALIDA_JSON)

    for nombre in revistas:
        if nombre in resultados:
            continue

        # Capitalizar título
        nombre_formateado = ' '.join([palabra.capitalize() for palabra in nombre.split()])

        try:
            print(f"Buscando: {nombre_formateado}")
            url_revista = obtener_url_revista(nombre_formateado)

            if not url_revista:
                print(f"No se encontró URL para: '{nombre_formateado}' (original: '{nombre}')")
                continue

            info = extraer_info_revista(url_revista)
            resultados[nombre] = info

            time.sleep(1)

        except Exception as e:
            print(f"ERROR {nombre}: {e}")

    guardar_resultados(resultados, SALIDA_JSON)
    print(f"Datos guardados en {SALIDA_JSON}")




# Prueba
def prueba_individual(nombre_original):
    nombre_formateado = ' '.join([palabra.capitalize() for palabra in nombre_original.split()])
    print(f"\nBuscando: {nombre_formateado}")

    url = obtener_url_revista(nombre_formateado)
    if not url:
        print(f"No se encontró URL para: {nombre_formateado}")
        return

    print(f"URL encontrada: {url}")
    info = extraer_info_revista(url)
    print(f"Información extraída para '{nombre_original}':\n")
    for k, v in info.items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    #main()
    prueba_individual("acta geophysica")
    prueba_individual("2d materials")