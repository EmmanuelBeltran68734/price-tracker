"""Lee las páginas guardadas en tests/fixtures/ y guarda sus precios en la base de datos."""

from pathlib import Path

from app.core.db import SesionLocal
from app.crawler.extractores import elegir_extractor
from app.crawler.repositorio import guardar_precio

FIXTURES = Path("tests/fixtures")

# (archivo guardado, URL real del producto)
PAGINAS = [
    (
        "exito_tv_lg.html",
        "https://www.exito.com/televisor-lg-75-pulgadas-qned-uhd-4k-smart-tv-75qned74bsa-3266510/p",
    ),
    (
        "alkosto_ps5.html",
        "https://www.alkosto.com/"
        "consola-ps5-digital-825-gb-hw-2115-1-control-inalambrico/p/711719023760",
    ),
]

with SesionLocal() as sesion:
    for archivo, url in PAGINAS:
        html = (FIXTURES / archivo).read_text(encoding="utf-8")
        datos = elegir_extractor(url).extraer(html)
        guardar_precio(sesion, url, datos)
        print(f"Guardado: {datos.nombre[:40]} -> ${datos.precio:,.0f}")
    sesion.commit()

print("Listo: los precios quedaron en la base de datos.")
