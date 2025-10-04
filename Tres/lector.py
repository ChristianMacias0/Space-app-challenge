import os
import xarray as xr
import matplotlib.pyplot as plt

# Carpeta donde están tus archivos descargados
CARPETA = "./TEMPO_downloads"

# Listar todos los archivos NetCDF
archivos = [os.path.join(CARPETA, f) for f in os.listdir(CARPETA) if f.endswith(".nc")]

if not archivos:
    print("No se encontraron archivos NetCDF en la carpeta.")
    exit()

# Abrir y combinar todos los archivos en un solo Dataset
print("Abriendo y combinando todos los archivos...")
ds_combined = xr.open_mfdataset(archivos, combine="by_coords")

# Mostrar información general
print(ds_combined)

# ====================================================================
# --- Visualización directa de todas las variables ---
# ====================================================================
for var in ds_combined.data_vars:
    data = ds_combined[var]
    print(f"\nVisualizando variable: {var}")
    
    # Si tiene dimensión de tiempo, calcular promedio sobre tiempo
    if "time" in data.dims:
        data_to_plot = data.mean(dim="time")
    else:
        data_to_plot = data

    plt.figure(figsize=(12,6))
    data_to_plot.plot(cmap="viridis")
    plt.title(f"{var} - promedio sobre tiempo si existía")
    plt.show()
