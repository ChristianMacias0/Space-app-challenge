Integración de `nasa_project` y `Tres`

Qué hice:
- Convertí los scripts en `Tres/` en funciones reutilizables.
- Añadí vistas en la app `air_quality` para llamarlas desde la web.
- Creé una plantilla simple `templates/air_quality/home.html` y la ruta `/`.
- Añadí endpoints: `/download/`, `/plot/`, `/excel/`.

Requisitos:
- Crear un entorno virtual e instalar dependencias:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

- Necesitas credenciales de Earthdata para `earthaccess.login()`.

Cómo probar:

1. Ejecuta el servidor Django:

    .\.venv\Scripts\Activate.ps1; python nasa_project\manage.py runserver

2. Abre http://127.0.0.1:8000/
3. Usa los enlaces "Iniciar descarga", "Generar plots" y "Generar y descargar Excel".

Notas:
- Las librerías científicas (xarray, pandas, matplotlib) deben instalarse en el entorno.
- Si no hay archivos NetCDF en `./TEMPO_downloads`, las funciones lanzarán errores claros.
- Para producción, agrega manejo de seguridad y no mantengas credenciales en el código.
# Space-app-challenge