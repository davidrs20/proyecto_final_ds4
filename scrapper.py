import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Configuración
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
SCIMAGO_BASE_URL = 'https://www.scimagojr.com'
SEARCH_URL = SCIMAGO_BASE_URL + '/journalsearch.php?q='
INPUT_JSON = 'datos/json/revistas.json'
OUTPUT_JSON = 'datos/json/revistas_scimagojr_extra.json'
MAX_REVISTAS = 15
UPDATE_PERIOD = 30  # días para re-scraping

# Carga inicial de datos existentes
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        revistas_data = json.load(f)
else:
    revistas_data = {}

# Función genérica de petición HTTP
def scrap(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response
        else:
            print(f"Warning: Status code {response.status_code} al acceder a {url}")
    except Exception as e:
        print(f"Error HTTP en {url}: {e}")
    return None

# Encontrar URL en SCImago
def find_journal_url(journal_title):
    search = SEARCH_URL + journal_title.replace(" ", "+")
    resp = scrap(search)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    result = soup.select_one('span.jrnlname')
    return SCIMAGO_BASE_URL + '/' + result.find_parent('a')['href'] if result else None

# Extraer áreas y categorías
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

# Generar widget SCImago
def obtener_widget(soup):
    try:
        img = soup.find('img', class_='imgwidget')
        if img and 'src' in img.attrs:
            src = img['src']
            journal_id = src.split('=')[-1]
            return (f'<a href="{SEARCH_URL}{journal_id}&amp;tip=sid&amp;exact=no" '
                    'title="SCImago Journal & Country Rank">'
                    f'<img border="0" src="https://www.scimagojr.com/{src}" '
                    'alt="SCImago Journal & Country Rank" /></a>')
    except Exception as e:
        print(f"Error al construir widget: {e}")
    return None

# Scrape SCImago
def scrape_journal_data(url):
    resp = scrap(url)
    if not resp:
        return {}
    soup = BeautifulSoup(resp.text, 'html.parser')
    data = {}
    # H-Index
    try:
        h2 = soup.find('h2', string=lambda s: s and 'H-Index' in s)
        data['h_index'] = h2.find_next_sibling('p').get_text(strip=True) if h2 else None
    except: data['h_index'] = None
    # Homepage
    try:
        a = soup.find('a', string='Homepage')
        data['website'] = a['href'] if a else None
    except: data['website'] = None
    # Publisher
    try:
        h2 = soup.find('h2', string=lambda s: s and 'Publisher' in s)
        data['publisher'] = h2.find_next_sibling('p').get_text(strip=True) if h2 else None
    except: data['publisher'] = None
    # ISSN
    try:
        h2 = soup.find('h2', string=lambda s: s and 'ISSN' in s)
        issn_text = h2.find_next_sibling('p').get_text(strip=True) if h2 else ''
        data['issn'] = [i.strip() for i in issn_text.split(',')] if issn_text else []
    except: data['issn'] = []
    # Publication type
    try:
        h2 = soup.find('h2', string=lambda s: s and 'Publication type' in s)
        data['publication_type'] = h2.find_next_sibling('p').get_text(strip=True) if h2 else None
    except: data['publication_type'] = None
    # Subject areas
    data['subjet_area_and_category'] = extract_subject_area(soup)
    # Widget
    data['widget'] = obtener_widget(soup)
    return data

# Comprobar necesidad de actualización
def needs_update(last_visit):
    try:
        last = datetime.strptime(last_visit, "%Y-%m-%d")
        return datetime.now() - last > timedelta(days=UPDATE_PERIOD)
    except:
        return True

# Proceso principal
with open(INPUT_JSON, 'r', encoding='utf-8') as f:
    revistas_input = json.load(f)

procesadas = 0
for revista in revistas_input:
    record = revistas_data.get(revista, {})
    last_visit = record.get('ultima_visita')
    if last_visit and not needs_update(last_visit):
        print(f"✓ No necesita actualizar: {revista}")
        continue
    if procesadas >= MAX_REVISTAS:
        print(f"Límite de {MAX_REVISTAS} alcanzado.")
        break
    print(f"→ Buscando: {revista}")
    url = find_journal_url(revista)
    if not url:
        print(f"✗ No hallado en SCImago: {revista}")
        continue
    info = scrape_journal_data(url)
    # Marca última visita
    info['ultima_visita'] = datetime.now().strftime("%Y-%m-%d")
    revistas_data[revista] = info
    print(f"✓ Procesado: {revista}")
    procesadas += 1
    time.sleep(2)

# Guardar resultados
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(revistas_data, f, indent=4, ensure_ascii=False)
print(f"✔ Completado. Revistas procesadas: {procesadas}")
