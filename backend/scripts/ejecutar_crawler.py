"""Ejecuta el crawler sobre todos los productos guardados (descarga de verdad)."""

import logging

from app.core.db import SesionLocal
from app.crawler.crawler import ejecutar_crawler, urls_registradas
from app.crawler.descargador import crear_cliente

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

with SesionLocal() as sesion, crear_cliente() as cliente:
    urls = urls_registradas(sesion)
    if not urls:
        print("No hay productos. Primero corre: uv run python -m scripts.guardar_precio_de_prueba")
    else:
        ejecutar_crawler(sesion, cliente, urls)
