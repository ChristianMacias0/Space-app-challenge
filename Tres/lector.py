import os
import xarray as xr
import matplotlib.pyplot as plt


def open_and_combine(folder: str = "./TEMPO_downloads"):
    """Abre y combina todos los archivos .nc en folder y devuelve un xarray.Dataset.

    Lanza FileNotFoundError si no hay archivos.
    """
    archivos = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".nc")]
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos NetCDF en la carpeta.")

    ds_combined = xr.open_mfdataset(archivos, combine="by_coords")
    return ds_combined


def open_and_plot(folder: str = "./TEMPO_downloads", out_folder: str = "./static/air_quality/plots"):
    """Abre los NetCDF en folder, genera una figura por variable y las guarda en out_folder.

    Devuelve la lista de rutas de archivos generados.
    """
    os.makedirs(out_folder, exist_ok=True)
    ds = open_and_combine(folder)

    saved = []
    for var in ds.data_vars:
        data = ds[var]
        if "time" in data.dims:
            data_to_plot = data.mean(dim="time")
        else:
            data_to_plot = data

        plt.figure(figsize=(10, 5))
        data_to_plot.plot(cmap="viridis")
        plt.title(f"{var}")
        out_path = os.path.join(out_folder, f"{var}.png")
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        saved.append(out_path)

    return saved

