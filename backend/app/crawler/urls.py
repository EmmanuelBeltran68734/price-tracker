"""Utilidades para URLs de productos."""

from urllib.parse import urlsplit, urlunsplit


def dominio_de(url: str) -> str:
    """Devuelve el dominio de una URL en minúsculas y sin "www.": "exito.com"."""
    return urlsplit(url.strip()).netloc.lower().removeprefix("www.")


def normalizar_url(url: str) -> str:
    """Deja la URL de un producto en una forma única, sin ?parámetros ni #ancla.

    Así, si dos usuarios pegan el mismo producto con distintos ?utm_..., se guarda una sola vez.
    """
    partes = urlsplit(url.strip())
    if partes.scheme not in ("http", "https") or not partes.netloc:
        raise ValueError(f"URL inválida: {url!r}")
    return urlunsplit(("https", partes.netloc.lower(), partes.path, "", ""))
