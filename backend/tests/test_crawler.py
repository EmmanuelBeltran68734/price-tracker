from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.crawler.crawler import ejecutar_crawler
from app.crawler.descargador import crear_cliente
from app.models import Base, HistorialPrecio

FIXTURES = Path(__file__).parent / "fixtures"
URL_EXITO = "https://www.exito.com/televisor-lg-75/p"
URL_ALKOSTO = "https://www.alkosto.com/consola-ps5/p/711719023760"

# El "internet falso": a cada URL le corresponde una página guardada
PAGINAS = {
    URL_EXITO: (FIXTURES / "exito_tv_lg.html").read_text(encoding="utf-8"),
    URL_ALKOSTO: (FIXTURES / "alkosto_ps5.html").read_text(encoding="utf-8"),
}


def responder(peticion):
    html = PAGINAS.get(str(peticion.url))
    if html is None:
        return httpx.Response(404)
    return httpx.Response(200, text=html)


@pytest.fixture
def sesion():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as sesion:
        yield sesion


@pytest.fixture
def cliente():
    return crear_cliente(transport=httpx.MockTransport(responder))


def no_esperar(segundos):
    pass


def test_crawler_guarda_los_precios_y_registra_la_ejecucion(sesion, cliente):
    ejecucion = ejecutar_crawler(sesion, cliente, [URL_EXITO, URL_ALKOSTO], dormir=no_esperar)

    precios = sesion.scalars(select(HistorialPrecio.precio).order_by(HistorialPrecio.id)).all()
    assert precios == [Decimal("3299900.00"), Decimal("2999000.00")]
    assert ejecucion.productos_ok == 2
    assert ejecucion.productos_con_error == 0
    assert ejecucion.errores is None
    assert ejecucion.terminado_en is not None


def test_un_producto_con_error_no_detiene_a_los_demas(sesion, cliente):
    url_rota = "https://www.exito.com/producto-que-ya-no-existe/p"

    ejecucion = ejecutar_crawler(sesion, cliente, [url_rota, URL_ALKOSTO], dormir=no_esperar)

    assert ejecucion.productos_ok == 1
    assert ejecucion.productos_con_error == 1
    assert "producto-que-ya-no-existe" in ejecucion.errores
    assert len(sesion.scalars(select(HistorialPrecio)).all()) == 1  # Alkosto sí se guardó


def test_espera_entre_peticiones(sesion, cliente):
    esperas = []
    ejecutar_crawler(sesion, cliente, [URL_EXITO, URL_ALKOSTO], dormir=esperas.append)
    assert esperas == [3.0]  # una pausa ENTRE las dos tiendas, no antes de la primera
