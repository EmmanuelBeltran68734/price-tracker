"""El crawler: recorre los productos, descarga sus páginas y guarda los precios."""

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawler.descargador import DescargaError, descargar
from app.crawler.extractores import ExtraccionError, TiendaNoSoportadaError, elegir_extractor
from app.crawler.repositorio import guardar_precio
from app.models import EjecucionCrawler, Producto

logger = logging.getLogger(__name__)

# Errores esperables de UN producto: se anotan y el crawler sigue con los demás.
ERRORES_POR_PRODUCTO = (DescargaError, ExtraccionError, TiendaNoSoportadaError, ValueError)


def urls_registradas(sesion: Session) -> list[str]:
    """Devuelve las URLs de todos los productos guardados en la base de datos."""
    return list(sesion.scalars(select(Producto.url).order_by(Producto.id)))


def ejecutar_crawler(
    sesion: Session,
    cliente: httpx.Client,
    urls: list[str],
    pausa: float = 3.0,
    dormir: Callable[[float], None] = time.sleep,
) -> EjecucionCrawler:
    """Revisa cada URL y registra la ejecución en ejecuciones_crawler."""
    ejecucion = EjecucionCrawler()
    sesion.add(ejecucion)
    errores = []

    for numero, url in enumerate(urls):
        if numero > 0:
            dormir(pausa)  # una petición cada pocos segundos: no saturar a las tiendas

        try:
            html = descargar(cliente, url, dormir=dormir)
            datos = elegir_extractor(url).extraer(html)
            guardar_precio(sesion, url, datos)
        except ERRORES_POR_PRODUCTO as error:
            logger.error("Error con %s: %s", url, error)
            errores.append(f"{url}: {error}")
        else:
            logger.info("OK %s -> $%s", datos.nombre[:40], datos.precio)

    ejecucion.productos_ok = len(urls) - len(errores)
    ejecucion.productos_con_error = len(errores)
    ejecucion.errores = "\n".join(errores) or None
    ejecucion.terminado_en = datetime.now(UTC)
    sesion.commit()

    logger.info(
        "Ejecución terminada: %d OK, %d con error.",
        ejecucion.productos_ok,
        ejecucion.productos_con_error,
    )
    return ejecucion
