from decimal import Decimal
from pathlib import Path

import pytest

from app.crawler.extractores import (
    ExtraccionError,
    JsonLdExtractor,
    MicrodataExtractor,
    TiendaNoSoportadaError,
    elegir_extractor,
)

FIXTURES = Path(__file__).parent / "fixtures"


def leer_fixture(nombre: str) -> str:
    """Lee una página guardada en tests/fixtures/ (sin internet)."""
    return (FIXTURES / nombre).read_text(encoding="utf-8")


# --- Elegir el extractor según la tienda ------------------------------------


@pytest.mark.parametrize(
    ("url", "clase_esperada"),
    [
        ("https://www.exito.com/televisor-lg-75/p", JsonLdExtractor),
        ("https://exito.com/televisor-lg-75/p", JsonLdExtractor),  # sin "www."
        ("https://www.alkosto.com/consola-ps5/p/711719023760", MicrodataExtractor),
        ("HTTPS://WWW.ALKOSTO.COM/consola-ps5/p/1", MicrodataExtractor),  # mayúsculas
    ],
)
def test_elegir_extractor_segun_la_tienda(url, clase_esperada):
    assert isinstance(elegir_extractor(url), clase_esperada)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.falabella.com.co/producto/123",  # tienda que aún no soportamos
        "https://exito.com.falso.co/p",  # se parece a Éxito, pero no lo es
        "esto no es una url",
    ],
)
def test_elegir_extractor_rechaza_tiendas_no_soportadas(url):
    with pytest.raises(TiendaNoSoportadaError):
        elegir_extractor(url)


# --- Extraer datos de páginas reales guardadas ------------------------------


def test_jsonld_lee_el_televisor_de_exito():
    producto = JsonLdExtractor().extraer(leer_fixture("exito_tv_lg.html"))

    assert producto.nombre == "Televisor LG 75 pulgadas QNED Uhd4K Smart TV 75QNED74BSA"
    assert producto.precio == Decimal("3299900.00")
    assert producto.moneda == "COP"
    assert producto.disponible is True
    assert producto.imagen_url.startswith("https://exitocol.vtexassets.com/")


def test_microdata_lee_la_consola_de_alkosto():
    producto = MicrodataExtractor().extraer(leer_fixture("alkosto_ps5.html"))

    assert producto.nombre.startswith("Consola PS5 Digital 825 GB")  # no "PLAYSTATION"
    assert producto.precio == Decimal("2999000.00")
    assert producto.moneda == "COP"
    assert producto.disponible is True
    assert producto.imagen_url.startswith("https://cdn.dam.alkosto.com/")  # URL limpia


@pytest.mark.parametrize(
    ("extractor", "fixture"),
    [
        (JsonLdExtractor(), "alkosto_ps5.html"),  # Alkosto no tiene JSON-LD de producto
        (MicrodataExtractor(), "exito_tv_lg.html"),  # Éxito no tiene microdata de producto
    ],
)
def test_extractor_equivocado_lanza_error(extractor, fixture):
    with pytest.raises(ExtraccionError):
        extractor.extraer(leer_fixture(fixture))


@pytest.mark.parametrize(
    ("url", "fixture", "precio"),
    [
        ("https://www.exito.com/televisor-lg-75/p", "exito_tv_lg.html", "3299900"),
        ("https://www.alkosto.com/consola-ps5/p/1", "alkosto_ps5.html", "2999000"),
    ],
)
def test_flujo_completo_url_a_producto(url, fixture, precio):
    extractor = elegir_extractor(url)
    producto = extractor.extraer(leer_fixture(fixture))
    assert producto.precio == Decimal(precio)
