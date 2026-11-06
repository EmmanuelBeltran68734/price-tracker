"""Extractores: leen el HTML de una página de producto y devuelven sus datos."""

import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

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


# --- Estrategia 2: microdata (Alkosto) -------------------------------------


class MicrodataExtractor(Extractor):
    """Lee las etiquetas itemprop dentro del bloque itemtype="schema.org/Product"."""

    def extraer(self, html: str) -> ProductoExtraido:
        soup = BeautifulSoup(html, "html.parser")
        producto = soup.find(itemtype=_es_tipo("Product"))
        if producto is None:
            raise ExtraccionError("La página no tiene un Product en microdata")

        oferta = _propiedad_tag(producto, "offers")
        nombre = _propiedad(producto, "name")
        precio = _propiedad(oferta, "price") if oferta else None
        if not nombre or precio is None:
            raise ExtraccionError("El Product de microdata no tiene nombre o precio")

        return ProductoExtraido(
            nombre=nombre,
            precio=normalizar_precio(precio),
            moneda=_propiedad(oferta, "priceCurrency") or "COP",
            disponible=_esta_disponible(_propiedad(oferta, "availability")),
            imagen_url=_limpiar_url(_propiedad(producto, "image")),
        )


def _es_tipo(tipo: str):
    return lambda valor: valor is not None and valor.endswith(f"schema.org/{tipo}")


def _propiedad_tag(scope: Tag, nombre: str) -> Tag | None:
    """Busca la etiqueta itemprop=nombre que pertenece directamente a este scope."""
    for tag in scope.find_all(itemprop=nombre):
        if tag.find_parent(itemscope=True) is scope:
            return tag
    return None


def _propiedad(scope: Tag, nombre: str) -> str | None:
    tag = _propiedad_tag(scope, nombre)
    if tag is None:
        return None
    valor = tag.get("content") or tag.get("href") or tag.get("src") or tag.get_text()
    return valor.strip() or None


def _limpiar_url(url: str | None) -> str | None:
    """Alkosto repite el dominio: 'https://www.alkosto.comhttps://cdn...'."""
    if not url:
        return None
    return url[url.rfind("https://") :]


# --- Elegir la estrategia según la tienda ----------------------------------


class TiendaNoSoportadaError(Exception):
    """La URL es de una tienda que todavía no sabemos leer."""


EXTRACTORES_POR_DOMINIO: dict[str, Extractor] = {
    "exito.com": JsonLdExtractor(),
    "alkosto.com": MicrodataExtractor(),
}


def elegir_extractor(url: str) -> Extractor:
    """Devuelve la estrategia de extracción que corresponde a la tienda de la URL."""
    dominio = urlparse(url).netloc.lower().removeprefix("www.")
    extractor = EXTRACTORES_POR_DOMINIO.get(dominio)
    if extractor is None:
        raise TiendaNoSoportadaError(f"Tienda no soportada: {dominio or url!r}")
    return extractor
