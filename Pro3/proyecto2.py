import os
import sys
import shutil
import glob
import pandas as pd
import numpy as np
import xarray as xr
import earthaccess
import plotly.express as px

# -------------------------------
# 1. CONFIGURACIÓN GENERAL
# -------------------------------
TEMPO_SHORT_NAME = "TEMPO_NO2_L2"
FECHA_INICIO = "2025-10-02 16:00:00"
FECHA_FIN = "2025-10-03 16:00:00"
BBOX_AREA = (-125.469, 15.820, -99.453, 35.859)

DATA_FOLDER = "./data"
DOWNLOAD_FOLDER = "./TEMPO_L2_downloads"
OUTPUT_CSV = "datos_tempo_limpios.csv"
OUTPUT_EXCEL = "datos_no2_agrupados.xlsx"
OUTPUT_HTML = "mapa_contaminacion_NO2.html"
MAPBOX_TOKEN = "TU_TOKEN_DE_MAPBOX"

CELL_SIZE = 0.11  # tamaño de celdas para agrupamiento

# Variables clave
VAR_NO2_TROPOSFERICO = "vertical_column_troposphere"
VAR_QA_VALUE = "main_data_quality_flag"
VAR_LAT_BOUNDS = "latitude_bounds"
VAR_LON_BOUNDS = "longitude_bounds"
GRUPOS_DATOS = ['/product']
GRUPOS_GEO = ['/geolocation']

# -------------------------------
# 2. FUNCIONES
# -------------------------------
def limpiar_directorio(folder):
    """Elimina TODO el contenido de la carpeta."""
    if os.path.exists(folder):
        print(f"🗑️ Limpiando {folder}...")
        for e in os.listdir(folder):
            ruta = os.path.join(folder, e)
            try:
                if os.path.isfile(ruta) or os.path.islink(ruta):
                    os.remove(ruta)
                elif os.path.isdir(ruta):
                    shutil.rmtree(ruta)
            except Exception as ex:
                print(f"❌ Error eliminando {ruta}: {ex}")
    else:
        os.makedirs(folder, exist_ok=True)
    print("✅ Carpeta lista.")

def descargar_datos():
    """Login y descarga archivos TEMPO, evitando duplicados y manejando errores."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    print("\n🔑 Iniciando sesión en NASA Earthdata...")
    try:
        earthaccess.login(persist=True)
    except Exception as e:
        print(f"❌ Error de login: {e}")
        return []

    print("\n🔎 Buscando archivos...")
    try:
        results = earthaccess.search_data(
            short_name=TEMPO_SHORT_NAME,
            temporal=(FECHA_INICIO, FECHA_FIN),
            bounding_box=BBOX_AREA
        )
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return []

    if not results:
        print("⚠️ No se encontraron archivos.")
        return []

    print(f"✅ {len(results)} archivos encontrados. Descargando...")
    descargados = []

    for i, f in enumerate(results, 1):
        try:
            archivos_descargados = earthaccess.download(f)  # Devuelve lista
            for archivo in archivos_descargados:
                nombre = os.path.basename(archivo)
                dest = os.path.join(DATA_FOLDER, nombre)
                
                if os.path.exists(dest):
                    print(f"  [{i}/{len(results)}] ⚠️ Ya existe: {nombre}, omitiendo descarga")
                    descargados.append(dest)
                    continue

                shutil.move(archivo, dest)
                descargados.append(dest)
                print(f"  [{i}/{len(results)}] Descargado: {nombre}")

        except Exception as e:
            print(f"⚠️ Error descargando archivo {i}: {e}")

    print(f"✅ Descargas completadas. Total archivos en carpeta: {len(descargados)}")
    return descargados
    """Login y descarga archivos TEMPO, manejando errores individuales correctamente."""
    limpiar_directorio(DATA_FOLDER)
    print("\n🔑 Iniciando sesión en NASA Earthdata...")
    try:
        earthaccess.login(persist=True)
    except Exception as e:
        print(f"❌ Error de login: {e}")
        return []
    
    print("\n🔎 Buscando archivos...")
    try:
        results = earthaccess.search_data(
            short_name=TEMPO_SHORT_NAME,
            temporal=(FECHA_INICIO, FECHA_FIN),
            bounding_box=BBOX_AREA
        )
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return []

    if not results:
        print("⚠️ No se encontraron archivos.")
        return []

    print(f"✅ {len(results)} archivos encontrados. Descargando...")
    descargados = []
    for i, f in enumerate(results, 1):
        try:
            archivos_descargados = earthaccess.download(f)  # Devuelve lista
            for archivo in archivos_descargados:
                dest = os.path.join(DATA_FOLDER, os.path.basename(archivo))
                shutil.move(archivo, dest)
                descargados.append(dest)
                print(f"  [{i}/{len(results)}] Descargado: {os.path.basename(archivo)}")
        except Exception as e:
            print(f"⚠️ Error descargando archivo {i}: {e}")
    print(f"✅ Descargas completadas. Total archivos: {len(descargados)}")
    return descargados
    """Login y descarga archivos TEMPO, manejando errores individuales."""
    limpiar_directorio(DATA_FOLDER)
    print("\n🔑 Iniciando sesión en NASA Earthdata...")
    try:
        earthaccess.login(persist=True)
    except Exception as e:
        print(f"❌ Error de login: {e}")
        return []
    
    print("\n🔎 Buscando archivos...")
    try:
        results = earthaccess.search_data(short_name=TEMPO_SHORT_NAME,
                                          temporal=(FECHA_INICIO, FECHA_FIN),
                                          bounding_box=BBOX_AREA)
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return []

    if not results:
        print("⚠️ No se encontraron archivos.")
        return []

    print(f"✅ {len(results)} archivos encontrados. Descargando...")
    descargados = []
    for i, f in enumerate(results, 1):
        try:
            archivo = earthaccess.download(f)
            if archivo:
                dest = os.path.join(DATA_FOLDER, os.path.basename(archivo))
                shutil.move(archivo, dest)
                descargados.append(dest)
                print(f"  [{i}/{len(results)}] Descargado: {os.path.basename(archivo)}")
        except Exception as e:
            print(f"⚠️ Error descargando archivo {i}: {e}")
    print(f"✅ Descargas completadas. Total archivos: {len(descargados)}")
    return descargados

def procesar_archivos(folder, output_csv):
    """Procesa los archivos .nc y filtra por calidad sin detenerse ante errores."""
    files = glob.glob(os.path.join(folder, "TEMPO_NO2_L2_*.nc"))
    if not files: 
        print("❌ No hay archivos para procesar."); return None

    datos = []
    for i, archivo in enumerate(files, 1):
        try:
            ds_prod = xr.open_dataset(archivo, group=GRUPOS_DATOS[0])
            ds_geo = xr.open_dataset(archivo, group=GRUPOS_GEO[0])
        except Exception as e:
            print(f"⚠️ No se pudo abrir {archivo}: {e}")
            continue

        if VAR_NO2_TROPOSFERICO not in ds_prod or VAR_LAT_BOUNDS not in ds_geo:
            print(f"⚠️ Variables faltantes en {archivo}. Omitiendo.")
            continue

        try:
            no2 = ds_prod[VAR_NO2_TROPOSFERICO].values
            qa = ds_prod[VAR_QA_VALUE].values
            lat = np.nanmean(ds_geo[VAR_LAT_BOUNDS].values, axis=2)
            lon = np.nanmean(ds_geo[VAR_LON_BOUNDS].values, axis=2)
            mask = qa == 0

            if np.sum(mask) == 0:
                print(f"⚠️ No hay datos de alta calidad en {archivo}.")
                continue

            df_temp = pd.DataFrame({
                "NO2_Troposferico": no2[mask].flatten(),
                "Latitud": lat[mask].flatten(),
                "Longitud": lon[mask].flatten(),
                "Archivo_Origen": os.path.basename(archivo)
            })
            datos.append(df_temp)
            print(f"  [{i}/{len(files)}] Procesado: {archivo} -> {len(df_temp)} puntos de alta calidad")
        except Exception as e:
            print(f"⚠️ Error procesando {archivo}: {e}")
            continue

    if datos:
        df_final = pd.concat(datos, ignore_index=True)
        df_final.to_csv(output_csv, index=False)
        print(f"✅ CSV generado: {output_csv} (total {len(df_final)} puntos)")
        return df_final
    else:
        print("❌ Ningún dato procesable encontrado.")
        return None

def agrupar_y_guardar(df, output_excel):
    """Agrupa por celdas geográficas y guarda Excel."""
    if df is None or df.empty:
        print("❌ No hay datos para agrupar."); return None
    df["lat_bin"] = (df["Latitud"] // CELL_SIZE) * CELL_SIZE
    df["lon_bin"] = (df["Longitud"] // CELL_SIZE) * CELL_SIZE
    grid = df.groupby(["lat_bin", "lon_bin"]).agg(NO2_promedio=("NO2_Troposferico","mean")).reset_index()
    grid.to_excel(output_excel, index=False)
    print(f"✅ Excel generado: {output_excel} (total {len(grid)} celdas)")
    return grid

def crear_mapa(df, output_html):
    """Crea mapa interactivo con Plotly."""
    if df is None or df.empty:
        print("❌ No hay datos para graficar."); return
    fig = px.scatter_mapbox(df, lat="lat_bin", lon="lon_bin",
                            color="NO2_promedio", size_max=15, zoom=3.5,
                            mapbox_style="carto-positron",
                            color_continuous_scale=px.colors.sequential.Inferno)
    fig.write_html(output_html)
    print(f"🎉 Mapa guardado: {output_html}")

# -------------------------------
# 3. EJECUCIÓN PRINCIPAL
# -------------------------------
if __name__ == "__main__":
    descargados = descargar_datos()
    df_csv = procesar_archivos(DATA_FOLDER, OUTPUT_CSV)
    df_agrupado = agrupar_y_guardar(df_csv, OUTPUT_EXCEL)
    crear_mapa(df_agrupado, OUTPUT_HTML)
