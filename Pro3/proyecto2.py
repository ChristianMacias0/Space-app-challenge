import os
import shutil
import glob
import pandas as pd
import numpy as np
import xarray as xr
import earthaccess
import plotly.express as px
from datetime import datetime, timedelta, timezone
import time

# -------------------------------
# 1. CONFIGURACIÓN GENERAL
# -------------------------------
TEMPO_SHORT_NAME = "TEMPO_NO2_L2"
BBOX_AREA = (-125.469, 15.820, -99.453, 35.859)

DATA_FOLDER = "./data"
OUTPUT_CSV = "datos_tempo_limpios.csv"
OUTPUT_EXCEL = "datos_no2_agrupados.xlsx"
OUTPUT_HTML = "mapa_contaminacion_NO2.html"
CELL_SIZE = 0.11  # tamaño de celdas para agrupamiento

VAR_NO2_TROPOSFERICO = "vertical_column_troposphere"
VAR_QA_VALUE = "main_data_quality_flag"
VAR_LAT_BOUNDS = "latitude_bounds"
VAR_LON_BOUNDS = "longitude_bounds"
GRUPOS_DATOS = ['/product']
GRUPOS_GEO = ['/geolocation']

# -------------------------------
# 2. FUNCIONES
# -------------------------------
def descargar_datos(fecha_inicio, fecha_fin):
    """Descarga archivos TEMPO evitando duplicados."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    try:
        earthaccess.login(persist=True)
    except Exception as e:
        print(f"❌ Error login: {e}")
        return []

    try:
        results = earthaccess.search_data(
            short_name=TEMPO_SHORT_NAME,
            temporal=(fecha_inicio, fecha_fin),
            bounding_box=BBOX_AREA
        )
    except Exception as e:
        print(f"❌ Error búsqueda: {e}")
        return []

    if not results:
        print("⚠️ No se encontraron archivos.")
        return []

    descargados = []
    for i, f in enumerate(results, 1):
        try:
            archivos_descargados = earthaccess.download(f)
            for archivo in archivos_descargados:
                nombre = os.path.basename(archivo)
                dest = os.path.join(DATA_FOLDER, nombre)
                if os.path.exists(dest):
                    print(f"  [{i}/{len(results)}] ⚠️ Ya existe: {nombre}")
                    continue
                shutil.move(archivo, dest)
                descargados.append(dest)
                print(f"  [{i}/{len(results)}] Descargado: {nombre}")
        except Exception as e:
            print(f"⚠️ Error descargando archivo {i}: {e}")
    return descargados

def procesar_archivo(archivo):
    """Procesa un archivo individual .nc y filtra por QA=0."""
    try:
        ds_prod = xr.open_dataset(archivo, group=GRUPOS_DATOS[0])
        ds_geo = xr.open_dataset(archivo, group=GRUPOS_GEO[0])
    except Exception as e:
        print(f"⚠️ No se pudo abrir {archivo}: {e}")
        return None

    if VAR_NO2_TROPOSFERICO not in ds_prod or VAR_LAT_BOUNDS not in ds_geo:
        print(f"⚠️ Variables faltantes en {archivo}, omitiendo.")
        return None

    lat_vals = ds_geo[VAR_LAT_BOUNDS].values
    lon_vals = ds_geo[VAR_LON_BOUNDS].values

    if lat_vals.size == 0 or lon_vals.size == 0:
        print(f"⚠️ Datos geográficos vacíos en {archivo}, omitiendo.")
        return None

    try:
        no2 = ds_prod[VAR_NO2_TROPOSFERICO].values
        qa = ds_prod[VAR_QA_VALUE].values
        lat = np.nanmean(lat_vals, axis=2)
        lon = np.nanmean(lon_vals, axis=2)
        mask = qa == 0

        if np.sum(mask) == 0:
            print(f"⚠️ No hay datos de alta calidad en {archivo}.")
            return None

        df_temp = pd.DataFrame({
            "NO2_Troposferico": no2[mask].flatten(),
            "Latitud": lat[mask].flatten(),
            "Longitud": lon[mask].flatten(),
            "Archivo_Origen": os.path.basename(archivo)
        })
        print(f"  Procesado: {archivo} -> {len(df_temp)} puntos de alta calidad")
        return df_temp
    except Exception as e:
        print(f"⚠️ Error procesando {archivo}: {e}")
        return None

def agrupar_y_guardar(df, output_excel):
    if df is None or df.empty:
        return None
    df["lat_bin"] = (df["Latitud"] // CELL_SIZE) * CELL_SIZE
    df["lon_bin"] = (df["Longitud"] // CELL_SIZE) * CELL_SIZE
    grid = df.groupby(["lat_bin", "lon_bin"]).agg(NO2_promedio=("NO2_Troposferico","mean")).reset_index()
    grid.to_excel(output_excel, index=False)
    print(f"✅ Excel generado: {output_excel} (total {len(grid)} celdas)")
    return grid

def crear_mapa(df, output_html):
    if df is None or df.empty:
        return
    fig = px.scatter_mapbox(df, lat="lat_bin", lon="lon_bin",
                            color="NO2_promedio", size_max=15, zoom=3.5,
                            mapbox_style="carto-positron",
                            color_continuous_scale=px.colors.sequential.Inferno)
    fig.write_html(output_html)
    print(f"🎉 Mapa guardado: {output_html}")

# -------------------------------
# 3. MONITOREO EN TIEMPO REAL OPTIMIZADO
# -------------------------------
if __name__ == "__main__":
    print("🚀 Monitoreo TEMPO NO2 cada 10 segundos (últimas 2 horas, archivos nuevos)...")
    archivos_procesados = set()  # guarda nombres de archivos ya procesados

    df_total = pd.DataFrame()

    while True:
        ahora = datetime.now(timezone.utc)
        fecha_inicio = ahora - timedelta(hours=2)
        fecha_fin = ahora

        # Descargar archivos nuevos
        descargados = descargar_datos(fecha_inicio, fecha_fin)

        # Filtrar solo archivos no procesados
        nuevos_archivos = [f for f in glob.glob(os.path.join(DATA_FOLDER, "TEMPO_NO2_L2_*.nc"))
                           if os.path.basename(f) not in archivos_procesados]

        if nuevos_archivos:
            for archivo in nuevos_archivos:
                df_nuevo = procesar_archivo(archivo)
                if df_nuevo is not None:
                    df_total = pd.concat([df_total, df_nuevo], ignore_index=True)
                archivos_procesados.add(os.path.basename(archivo))

            # Guardar CSV actualizado
            if not df_total.empty:
                df_total.to_csv(OUTPUT_CSV, index=False)
                print(f"✅ CSV actualizado: {OUTPUT_CSV} (total {len(df_total)} puntos)")

            # Guardar Excel agrupado y mapa
            df_agrupado = agrupar_y_guardar(df_total, OUTPUT_EXCEL)
            crear_mapa(df_agrupado, OUTPUT_HTML)
        else:
            print("⏳ No hay archivos nuevos para procesar.")

        print("⏱ Esperando 10 segundos para la siguiente actualización...\n")
        time.sleep(10)
