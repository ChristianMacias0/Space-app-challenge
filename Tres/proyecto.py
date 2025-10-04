import earthaccess
import os
import sys
import shutil

# ====================================================================
# --- 1. Configuración de la Búsqueda ---
# ====================================================================
TEMPO_SHORT_NAME = "TEMPO_NO2_L3"
FECHA_INICIO = "2025-09-01 16:00:00"
FECHA_FIN = "2025-09-01 17:00:00"
BBOX_AREA = (-125.469, 15.820, -99.453, 35.859)

# Carpeta donde guardar los archivos descargados
DOWNLOAD_FOLDER = "./TEMPO_downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ====================================================================
# --- 2. Autenticación ---
# ====================================================================
print("Iniciando sesión en NASA Earthdata...")
try:
    auth = earthaccess.login(persist=True)
except Exception as e:
    print(f"Error de autenticación: {e}")
    sys.exit()

# ====================================================================
# --- 3. Búsqueda ---
# ====================================================================
print("Buscando archivos de TEMPO...")
try:
    search_results = earthaccess.search_data(
        short_name=TEMPO_SHORT_NAME,
        temporal=(FECHA_INICIO, FECHA_FIN),
        bounding_box=BBOX_AREA
    )

    if not search_results:
        print("No se encontraron archivos para los criterios especificados.")
        sys.exit()

    print(f"Se encontraron {len(search_results)} archivos de TEMPO.")

except Exception as e:
    print(f"Error durante la búsqueda: {e}")
    sys.exit()

# ====================================================================
# --- 4. Descarga de todos los archivos ---
# ====================================================================
print("Descargando todos los archivos...")
try:
    downloaded_files = earthaccess.download(search_results)

    if downloaded_files:
        # Mover los archivos descargados a la carpeta deseada
        moved_files = []
        for f in downloaded_files:
            dest = os.path.join(DOWNLOAD_FOLDER, os.path.basename(f))
            shutil.move(f, dest)
            moved_files.append(dest)
        print(f"Descarga completada. Archivos guardados en {DOWNLOAD_FOLDER}")
        for f in moved_files:
            print("-", f)
    else:
        print("No se descargó ningún archivo.")

except Exception as e:
    print(f"Ocurrió un error durante la descarga: {e}")
    sys.exit()
