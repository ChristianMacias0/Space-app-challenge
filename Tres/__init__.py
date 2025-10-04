"""Paquete Tres: funciones reutilizables para descarga y procesamiento de TEMPO."""
from .proyecto import download_tempo
from .lector import open_and_plot, open_and_combine
from .excel import generate_reduced_excel
from .co2 import extract_co2

__all__ = [
    "download_tempo",
    "open_and_plot",
    "open_and_combine",
    "generate_reduced_excel",
    "extract_co2",
]
