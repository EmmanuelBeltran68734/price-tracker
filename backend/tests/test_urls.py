import pytest

from app.crawler.urls import dominio_de, normalizar_url


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        (
            "https://www.exito.com/tv-lg/p?utm_source=facebook&utm_medium=social",
            "https://www.exito.com/tv-lg/p",
        ),  # quita parámetros de seguimiento
        ("https://www.exito.com/tv-lg/p#opiniones", "https://www.exito.com/tv-lg/p"),  # quita #
        ("http://www.alkosto.com/ps5/p/1", "https://www.alkosto.com/ps5/p/1"),  # http -> https
        ("https://WWW.ALKOSTO.COM/Consola/p/1", "https://www.alkosto.com/Consola/p/1"),
        ("  https://www.exito.com/tv-lg/p  ", "https://www.exito.com/tv-lg/p"),  # espacios
    ],
)
def test_normalizar_url(url, esperada):
    assert normalizar_url(url) == esperada


@pytest.mark.parametrize("url", ["", "esto no es una url", "/solo/la/ruta", "ftp://exito.com/p"])
def test_normalizar_url_rechaza_urls_invalidas(url):
    with pytest.raises(ValueError):
        normalizar_url(url)


@pytest.mark.parametrize(
    ("url", "dominio"),
    [
        ("https://www.exito.com/tv/p", "exito.com"),
        ("https://exito.com/tv/p", "exito.com"),
        ("HTTPS://WWW.ALKOSTO.COM/ps5/p/1", "alkosto.com"),
        ("esto no es una url", ""),
    ],
)
def test_dominio_de(url, dominio):
    assert dominio_de(url) == dominio
