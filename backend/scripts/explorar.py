"""Scripts de exploración: descarga páginas de producto y muestra cómo responde"""

import time
from pathlib import Path

import httpx

USER_AGENT = "PriceTrackerBot/1.0 (+https://github.com/EmmanuelBeltran68734/price-tracker)"

PRODUCTOS = {
    "alkosto": "https://www.alkosto.com/consola-ps5-digital-825-gb-hw-2115-1-control-inalambrico/p/711719023760",
    "exito": "https://www.exito.com/televisor-lg-75-pulgadas-qned-uhd-4k-smart-tv-75qned74bsa-3266510/p",
}

CARPETA_SALIDA = Path(__file__).parent / "salida"
ESPERA_ENTRE_PETICIONES = 3  # segundos


def descargar(url: str) -> httpx.Response:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "es-CO,es;q=0.9",
    }
    return httpx.get(url, headers=headers, timeout=20, follow_redirects=True)


def main() -> None:
    CARPETA_SALIDA.mkdir(exist_ok=True)

    for tienda, url in PRODUCTOS.items():
        print(f"\n=== {tienda.upper()} ===")
        respuesta = descargar(url)
        html = respuesta.text

        print(f"Estado: {respuesta.status_code}")
        print(f"tamaño del HTML: {len(html):,} caracteres")
        print(f"¿Tiene JSON-LD?: {'application/ld+json' in html}")

        archivo = CARPETA_SALIDA / f"{tienda}.html"
        archivo.write_text(html, encoding="utf-8")
        print(f"HTML guardado en: {archivo}")

        time.sleep(ESPERA_ENTRE_PETICIONES)


if __name__ == "__main__":
    main()
