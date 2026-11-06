import pytest

from app.crawler.extractores import (
    JsonLdExtractor,
    MicrodataExtractor,
    TiendaNoSoportadaError,
    elegir_extractor,
)


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
