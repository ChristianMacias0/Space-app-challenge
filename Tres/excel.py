import os
import xarray as xr
import pandas as pd


def generate_reduced_excel(
    input_folder: str = "./TEMPO_downloads",
    output_excel: str = "TEMPO_datos_reducidos.xlsx",
    variables: list | None = None,
    lat_step: int = 5,
    lon_step: int = 5,
):
    """Genera un Excel reducido a partir de los NetCDF en input_folder.

    Devuelve la ruta al archivo Excel generado.
    """
    if variables is None:
        variables = ["NO2", "weight"]

    archivos = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".nc")]
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos.")

    xr.set_options(use_new_combine_var=True)
    ds_combined = xr.open_mfdataset(archivos, combine="by_coords")

    vars_available = [v for v in variables if v in ds_combined.data_vars]
    if not vars_available:
        raise ValueError("No se encontraron las variables solicitadas en los datasets.")

    if "time" in ds_combined.dims:
        ds_reducido = ds_combined.isel(time=0)[vars_available]
    else:
        ds_reducido = ds_combined[vars_available]

    ds_reducido = ds_reducido.isel(lat=slice(None, None, lat_step), lon=slice(None, None, lon_step))

    df = ds_reducido.to_dataframe().reset_index()
    df.to_excel(output_excel, index=False)
    return output_excel

