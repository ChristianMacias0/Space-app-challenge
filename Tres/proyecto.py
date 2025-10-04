import earthaccess
import os
import sys
import shutil

import json
from pathlib import Path


def download_tempo(
    tempo_short_name: str = "TEMPO_NO2_L3",
    fecha_inicio: str = "2025-09-01 16:00:00",
    fecha_fin: str = "2025-09-01 17:00:00",
    bbox_area: tuple = (-125.469, 15.820, -99.453, 35.859),
    download_folder: str = "./TEMPO_downloads",
    status_file: str | None = None,
    use_auth: bool = True,
):
    """Descarga archivos TEMPO desde Earthdata y los mueve a download_folder.

    Si status_file es None, crea `static/air_quality/download_status.json` dentro
    del paquete para comunicar el estado a la app web.

    use_auth=False intenta realizar búsqueda/descarga sin llamar a earthaccess.login().
    Devuelve la lista de archivos descargados.
    """
    os.makedirs(download_folder, exist_ok=True)

    # Preparar archivo de estado si se solicita
    if status_file is None:
        repo_root = Path(__file__).resolve().parents[1]
        default_status_dir = repo_root / 'static' / 'air_quality'
        default_status_dir.mkdir(parents=True, exist_ok=True)
        status_file = str(default_status_dir / 'download_status.json')

    def write_status(state: str, files: list | None = None, message: str | None = None):
        payload = {"state": state, "files": files or [], "message": message}
        try:
            with open(status_file, 'w', encoding='utf-8') as fh:
                json.dump(payload, fh)
        except Exception:
            pass

    write_status('pending')

    # Autenticación
    if use_auth:
        try:
            auth = earthaccess.login(persist=True)
        except Exception as e:
            write_status('error', message=f"Error de autenticación: {e}")
            raise RuntimeError(f"Error de autenticación: {e}")
    else:
        auth = None

    # Búsqueda
    try:
        search_results = earthaccess.search_data(
            short_name=tempo_short_name,
            temporal=(fecha_inicio, fecha_fin),
            bounding_box=bbox_area,
        )

        if not search_results:
            write_status('done', files=[])
            return []

        write_status('running')

    except Exception as e:
        write_status('error', message=str(e))
        raise RuntimeError(f"Error durante la búsqueda: {e}")

    # Descarga de todos los archivos
    try:
        downloaded_files = earthaccess.download(search_results)

        moved_files = []
        if downloaded_files:
            for f in downloaded_files:
                dest = os.path.join(download_folder, os.path.basename(f))
                shutil.move(f, dest)
                moved_files.append(dest)
            write_status('done', files=moved_files)
        else:
            write_status('done', files=[])

        return moved_files

    except Exception as e:
        write_status('error', message=str(e))
        raise RuntimeError(f"Ocurrió un error durante la descarga: {e}")


if __name__ == "__main__":
    try:
        files = download_tempo()
        print("Archivos:", files)
    except Exception as e:
        print(e)
