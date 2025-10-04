import os
import xarray as xr
import pandas as pd

CARPETA = "./TEMPO_downloads"
EXCEL_SALIDA = "TEMPO_datos_reducidos.xlsx"

archivos = [os.path.join(CARPETA, f) for f in os.listdir(CARPETA) if f.endswith(".nc")]

if not archivos:
    print("No se encontraron archivos.")
    exit()

# Abrir y combinar archivos
xr.set_options(use_new_combine_var=True)
ds_combined = xr.open_mfdataset(archivos, combine="by_coords")

# Seleccionar solo variables de interés
variables = ["NO2", "weight"]
variables = [v for v in variables if v in ds_combined.data_vars]

# Reducir a un solo tiempo (primer gránulo)
if "time" in ds_combined.dims:
    ds_reducido = ds_combined.isel(time=0)[variables]
else:
    ds_reducido = ds_combined[variables]

# Submuestreo espacial: tomar cada 5º pixel
ds_reducido = ds_reducido.isel(lat=slice(None, None, 5), lon=slice(None, None, 5))

# Convertir a DataFrame y guardar en Excel
df = ds_reducido.to_dataframe().reset_index()
df.to_excel(EXCEL_SALIDA, index=False)
print(f"Excel reducido generado: {EXCEL_SALIDA}")
print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
