from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
import sys
from pathlib import Path
import importlib
import json
from django.http import JsonResponse

# Asegurar que la carpeta raíz del repo está en sys.path para poder importar Tres
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def home(request):
    """Página principal que muestra las imágenes generadas (si existen)."""
    plots_dir = os.path.join(settings.BASE_DIR, 'static', 'air_quality', 'plots')
    images = []
    if os.path.isdir(plots_dir):
        images = [f for f in os.listdir(plots_dir) if f.endswith('.png')]

    return render(request, 'air_quality/home.html', {'images': images})


def trigger_download(request):
    try:
        proyecto = importlib.import_module('Tres.proyecto')
        # lanzar descarga sin forzar login interactivo si se desea
        use_auth = True
        # Si se pasa ?noauth=1 en la URL, intentamos sin login
        if request.GET.get('noauth') == '1':
            use_auth = False
        files = proyecto.download_tempo(use_auth=use_auth)
    except Exception as e:
        return HttpResponse(f"Error durante la descarga: {e}")

    return HttpResponse(f"Descarga finalizada. Archivos: {files}")


def status(request):
    # lee el archivo status JSON generado por download_tempo
    status_file = os.path.join(settings.BASE_DIR, 'static', 'air_quality', 'download_status.json')
    if not os.path.exists(status_file):
        return JsonResponse({'state': 'unknown', 'files': [], 'message': None})

    try:
        with open(status_file, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception as e:
        return JsonResponse({'state': 'error', 'files': [], 'message': str(e)})

    return JsonResponse(data)


def trigger_plot(request):
    try:
        lector = importlib.import_module('Tres.lector')
        saved = lector.open_and_plot()
    except Exception as e:
        return HttpResponse(f"Error al plotear: {e}")

    return redirect('home')


def trigger_excel(request):
    try:
        excel_mod = importlib.import_module('Tres.excel')
        excel_path = excel_mod.generate_reduced_excel()
    except Exception as e:
        return HttpResponse(f"Error al generar Excel: {e}")

    # Devolver el archivo para descarga si existe
    if os.path.exists(excel_path):
        return FileResponse(open(excel_path, 'rb'), as_attachment=True, filename=os.path.basename(excel_path))
    return HttpResponse("Excel no generado.")
