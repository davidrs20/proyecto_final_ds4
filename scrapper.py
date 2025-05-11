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
MAX_REVISTAS = 50  # Cambia este valor si necesitas otro límite

# Cargar revistas ya obtenidas
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        revistas_data = json.load(f)
else:
    revistas_data = {}

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

def obtenerimagen(soup):
    try:
        img = soup.find('img', class_='imgwidget')
        if img and 'src' in img.attrs:
            return 'https://www.scimagojr.com/' + img['src']
    except Exception as e:
        print(f"Error al extraer imagen: {e}")
    return None

def extract_subject_area(soup):
    section = soup.find("h2", string="Subject Area and Category")
    if not section:
        return None
    table = section.find_next("table")
    if not table:
        return None
    items = table.find_all("td")
    categories = [td.get_text(strip=True) for td in items if td]
    return ', '.join(categories)

def scrape_journal_data(url):
    soup = BeautifulSoup(scrap(url).text, 'html.parser')

    # Obtener H-Index
    try:
        h_index_section = soup.find('h2', string=lambda s: s and 'H-Index' in s)
        h_index = h_index_section.find_next_sibling('p').text.strip() if h_index_section else None
    except Exception as e:
        print(f"Error al extraer H-Index: {e}")
        h_index = None

    # Obtener Homepage
    try:
        homepage_section = soup.find('a', string='Homepage')
        homepage_link = homepage_section['href'] if homepage_section else None
    except Exception as e:
        print(f"Error al extraer Homepage: {e}")
        homepage_link = None

    # Obtener Publisher
    try:
        publisher_section = soup.find('h2', string=lambda s: s and 'Publisher' in s)
        publisher = publisher_section.find_next_sibling('p').text.strip() if publisher_section else None
    except Exception as e:
        print(f"Error al extraer Publisher: {e}")
        publisher = None

    # Obtener ISSN
    try:
        issn_section = soup.find('h2', string=lambda s: s and 'ISSN' in s)
        issn = issn_section.find_next_sibling('p').text.strip() if issn_section else None
    except Exception as e:
        print(f"Error al extraer ISSN: {e}")
        issn = None

    # Obtener imagen del widget
    widget_url = obtenerimagen(soup)

    # Obtener Publication Type
    try:
        publication_type_section = soup.find('h2', string=lambda s: s and 'Publication type' in s)
        publication_type = publication_type_section.find_next_sibling('p').text.strip() if publication_type_section else None
    except Exception as e:
        print(f"Error al extraer Publication type: {e}")
        publication_type = None

    return {
        "site": homepage_link,
        "h_index": h_index,
        "subject_area_category": extract_subject_area(soup),
        "publisher": publisher,
        "issn": issn,
        "widget": widget_url,
        "publication_type": publication_type,
        "url": url
    }

# Cargar títulos a procesar
with open(INPUT_JSON, 'r', encoding='utf-8') as f:
    revistas_input = json.load(f)

procesadas = 0
for revista in revistas_input:
    if revista in revistas_data:
        print(f"✓ Ya existe: {revista}")
        continue

    if procesadas >= MAX_REVISTAS:
        print(f"🚫 Límite de {MAX_REVISTAS} revistas alcanzado.")
        break

    print(f"→ Buscando: {revista}")
    try:
        url = find_journal_url(revista)
        if not url:
            print(f"✗ No se encontró URL para {revista}")
            continue

        info = scrape_journal_data(url)
        revistas_data[revista] = info
        print(f"✓ Datos obtenidos para {revista}")
        procesadas += 1
        time.sleep(2)
    except Exception as e:
        print(f"✗ Error con {revista}: {e}")

# Guardar archivo actualizado
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(revistas_data, f, indent=4, ensure_ascii=False)

print(f"✔ Proceso completado. Revistas nuevas procesadas: {procesadas}")