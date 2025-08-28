=====================================================
🔥 FIRMS Pipeline - Análisis de focos de calor NASA
=====================================================

Este proyecto descarga y procesa datos de focos de calor desde FIRMS (NASA) usando su API pública. Está preparado para ejecutarse desde cero en cualquier máquina con Python instalado.

--------------------------
📦 1. REQUISITOS DEL SISTEMA
--------------------------

- Python 3.9 o superior
- pip
- Acceso a Internet
- Un editor de texto (VS Code, Notepad++, etc.)


----------------------------------
🚀 2. INSTRUCCIONES DE INSTALACIÓN
----------------------------------

1. Descomprime el archivo ZIP en una carpeta local.

2. Abre una terminal o consola en esa carpeta.

3. (Opcional, pero recomendado) Crea un entorno virtual:

   - En Windows (cmd):
     > python -m venv .venv
     > .venv\Scripts\activate

   - En Linux/macOS:
     $ python3 -m venv .venv
     $ source .venv/bin/activate

4. Instala todas las dependencias necesarias:

   > pip install -r requirements.txt


-------------------------------------------------
🔑 3. CONFIGURACIÓN DEL ARCHIVO DE CREDENCIALES
-------------------------------------------------

El proyecto usa un archivo `.env` para guardar de forma segura tu clave de API (API_KEY) de FIRMS.

1. Ve al sitio oficial para obtener tu MAP_KEY gratuito (si aún no lo tienes):

   https://firms.modaps.eosdis.nasa.gov/api/

2. Edita un archivo llamado **`.env`** en la carpeta raíz del proyecto y modifica los parámetros que quieras en el archivo settings.yaml en la carpeta config


ejecuta el proyecto corriendo el archivo main.py
