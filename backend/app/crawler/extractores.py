"""Extractores: leen el HTML de una página de producto y devuelven sus datos."""

import json
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from app.crawler.modelos import ProductoExtraido
from app.crawler.precios import normalizar_precio

ESTADOS_DISPONIBLES = {"InStock", "LimitedAvailability", "OnlineOnly", "PreOrder"}


class ExtraccionError(Exception):
    """No se pudieron leer los datos del producto en la página."""


class Extractor(ABC):
    """Molde común: toda estrategia de extracción debe tener el método extraer()."""

    @abstractmethod
    def extraer(self, html: str) -> ProductoExtraido:
        """Lee el HTML de una página de producto y devuelve sus datos."""


# --- Estrategia 1: JSON-LD (Éxito) -----------------------------------------


class JsonLdExtractor(Extractor):
    """Lee el bloque <script type="application/ld+json"> con @type Product."""

    def extraer(self, html: str) -> ProductoExtraido:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                datos = json.loads(script.string or "")
            except json.JSONDecodeError:
                continue
            producto = _buscar_producto_jsonld(datos)
            if producto is not None:
                return _producto_desde_jsonld(producto)
        raise ExtraccionError("La página no tiene un Product en JSON-LD")


def _buscar_producto_jsonld(datos: dict | list) -> dict | None:
    candidatos = datos if isinstance(datos, list) else datos.get("@graph", [datos])
    for item in candidatos:
        if isinstance(item, dict) and item.get("@type") == "Product":
            return item
    return None


def _producto_desde_jsonld(producto: dict) -> ProductoExtraido:
    ofertas = producto.get("offers") or {}
    oferta = ofertas[0] if isinstance(ofertas, list) and ofertas else ofertas
    precio = oferta.get("price", oferta.get("lowPrice"))
    nombre = producto.get("name")
    if not nombre or precio is None:
        raise ExtraccionError("El Product de JSON-LD no tiene nombre o precio")

    imagen = producto.get("image")
    if isinstance(imagen, list):
        imagen = imagen[0] if imagen else None

    return ProductoExtraido(
        nombre=nombre.strip(),
        precio=normalizar_precio(precio),
        moneda=oferta.get("priceCurrency", "COP"),
        disponible=_esta_disponible(oferta.get("availability")),
        imagen_url=imagen,
    )


def _esta_disponible(availability: str | None) -> bool:
    if not availability:
        return True
    estado = availability.rsplit("/", 1)[-1]
    return estado in ESTADOS_DISPONIBLES
