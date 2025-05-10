import os
import json
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

SCIMAGO_BASE_URL = 'https://www.scimagojr.com'
SEARCH_URL = SCIMAGO_BASE_URL + '/journalsearch.php?q='
INPUT_JSON = 'datos/json/revistas.json'
OUTPUT_JSON = 'datos/json/revistas_scimagojr.json'

# Cargar revistas existentes
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        revistas_data = json.load(f)
else:
    revistas_data = {}

# Funciones utilitarias
def scrap(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code} en {url}")
    return response

def find_journal_url(journal_title):
    search = SEARCH_URL + journal_title.replace(" ", "+")
    soup = BeautifulSoup(scrap(search).text, 'html.parser')
    result = soup.select_one('span.jrnlname')
    if result:
        return SCIMAGO_BASE_URL + '/' + result.find_parent('a')['href']
    return None

def scrape_journal_data(url):
    soup = BeautifulSoup(scrap(url).text, 'html.parser')
    
    try:
        h_index = soup.find('h2', string='H-Index').find_next_sibling('p').text.strip()
    except:
        h_index = None
    
    def extract_td(label):
        td = soup.find('td', string=label)
        return td.find_next_sibling('td').text.strip() if td else None

    return {
        "site": extract_td("Homepage"),
        "h_index": h_index,
        "subject_area_category": extract_td("Subject Area and Category"),
        "publisher": extract_td("Publisher"),
        "issn": extract_td("ISSN"),
        "widget": extract_td("Widget"),
        "publication_type": extract_td("Publication Type"),
        "url": url
    }

# Cargar revistas desde el archivo original
with open(INPUT_JSON, 'r', encoding='utf-8') as f:
    revistas_input = json.load(f)

# Procesar cada revista (máximo 100 nuevas búsquedas)
busquedas_realizadas = 0
MAX_BUSQUEDAS = 100

for revista in revistas_input:
    if revista in revistas_data:
        print(f"✓ Ya existe: {revista}")
        continue

    if busquedas_realizadas >= MAX_BUSQUEDAS:
        print("🔁 Límite de 100 búsquedas alcanzado.")
        break

    print(f"→ Buscando: {revista}")
    try:
        url = find_journal_url(revista)
        if not url:
            print(f"✗ No se encontró URL para {revista}")
            continue

        info = scrape_journal_data(url)
        revistas_data[revista] = info
        busquedas_realizadas += 1
        print(f"✓ Datos obtenidos para {revista}")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Error con {revista}: {e}")

# Guardar los datos actualizados
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(revistas_data, f, indent=4, ensure_ascii=False)

print("✔ Proceso completado.")
