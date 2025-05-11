Proyecto final desarrollo 4

Integrantes:
1. Alan Joaquin Hernández López.
2. Jesús David Rosales Salomón.
3. Jesús Ulises Tiznado Ruiz.

Este proyecto permite explorar y consultar un catálogo de revistas académicas obtenidas a partir de archivos CSV y enriquecidas con información extraída del portal [SCImago Journal Rank](https://www.scimagojr.com/), mediante scraping web.

La interfaz está desarrollada en **Python + Flask + Bootstrap**, siguiendo los colores y diseño institucional de la **Universidad de Sonora**.

### Parte 1 – Generación del JSON Base
Lee múltiples archivos CSV desde las carpetas `datos/csv/areas/` y `datos/csv/catalogos/`, y genera un archivo JSON en `datos/json/`, con una estructura como:

```json
{
  "acta geophysica": {
    "areas": ["CIENCIAS_EXA", "ING"],
    "catalogos": ["JCR", "SCOPUS"]
  },
  "acta geophysica sinica": {
    "areas": ["CIENCIAS_EXA"],
    "catalogos": ["SCOPUS"]
  }
}

 Parte 2 – Web Scraper desde SCImago
Lee el archivo JSON generado en la parte 1, busca en línea información sobre cada revista (sólo si no está ya guardada), y genera un segundo archivo JSON con información como:

Sitio web
H-Index
Área y Categoría
Editor
ISSN
Widget
Tipo de publicación
Este archivo es el que usará el sitio Flask como base de datos estática.

Parte 3 – Sitio Web Flask
Muestra una página web navegable que permite explorar las revistas por:

Catálogo
Área
Abecedario
Búsqueda libre
Cada vista muestra tablas dinámicas con Bootstrap y permite acceder a la información completa de cada revista. Además, se incluye una sección de créditos.


*** Instalación y Ejecución
 git clone https://github.com/usuario/repositorio-revistas.git
cd repositorio-revistas

Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

 Instala las dependencias
 pip install -r requirements.txt

 Ejecuta el proyecto
 python app.py

**Extras:
- Agregar un logotipo con nombre del sistema / página 
- Agregar un campo o llave "ultima_visita" que cuente con fecha de última visita a scimagojr.com, si la fecha es mayor a 1 mes (u otro periodo), que el sistema actualice la información. 
