"""Descarga páginas de las tiendas con reintentos y espera exponencial."""

import logging
import time
from collections.abc import Callable

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "PriceTrackerBot/0.1 (+https://github.com/EmmanuelBeltran68734/price-tracker)"

# Errores temporales: vale la pena volver a intentar. Un 404, en cambio, no se arregla solo.
CODIGOS_REINTENTABLES = {429, 500, 502, 503, 504}


class DescargaError(Exception):
    """No se pudo descargar la página."""


def crear_cliente(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    """Cliente HTTP que se identifica honestamente y no espera para siempre."""
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=20.0,
        follow_redirects=True,
        transport=transport,
    )


def descargar(
    cliente: httpx.Client,
    url: str,
    intentos: int = 3,
    espera_base: float = 2.0,
    dormir: Callable[[float], None] = time.sleep,
) -> str:
    """Descarga el HTML de una URL. Si falla por un error temporal, reintenta.

    Entre intentos espera cada vez el doble: 2 s, 4 s, 8 s... (espera exponencial).
    """
    for intento in range(1, intentos + 1):
        try:
            respuesta = cliente.get(url)
        except httpx.TransportError as error:
            motivo = f"error de red ({type(error).__name__})"
        else:
            if respuesta.is_success:
                return respuesta.text
            if respuesta.status_code not in CODIGOS_REINTENTABLES:
                raise DescargaError(f"HTTP {respuesta.status_code} en {url}")
            motivo = f"HTTP {respuesta.status_code}"

        if intento < intentos:
            espera = espera_base * 2 ** (intento - 1)
            logger.warning(
                "Intento %d de %d falló: %s. Reintento en %.0f s.",
                intento,
                intentos,
                motivo,
                espera,
            )
            dormir(espera)

    raise DescargaError(f"Falló después de {intentos} intentos ({motivo}): {url}")
