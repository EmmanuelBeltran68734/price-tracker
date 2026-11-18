import httpx
import pytest

from app.crawler.descargador import DescargaError, crear_cliente, descargar

URL = "https://www.exito.com/tv-lg/p"


def cliente_falso(respuestas):
    """Cliente HTTP que NO usa internet: contesta con la lista dada, en orden.

    Cada elemento es un código HTTP (200, 503...) o una excepción para simular un error de red.
    """
    pendientes = iter(respuestas)
    peticiones = []

    def responder(peticion):
        peticiones.append(peticion)
        respuesta = next(pendientes)
        if isinstance(respuesta, Exception):
            raise respuesta
        return httpx.Response(respuesta, text=f"<html>{respuesta}</html>")

    return crear_cliente(transport=httpx.MockTransport(responder)), peticiones


class RelojFalso:
    """Reemplaza a time.sleep: anota cuánto habría esperado, sin esperar de verdad."""

    def __init__(self):
        self.esperas = []

    def __call__(self, segundos):
        self.esperas.append(segundos)


def test_descarga_a_la_primera():
    cliente, peticiones = cliente_falso([200])
    reloj = RelojFalso()

    assert descargar(cliente, URL, dormir=reloj) == "<html>200</html>"
    assert len(peticiones) == 1
    assert reloj.esperas == []  # no tuvo que esperar


def test_se_identifica_con_user_agent_propio():
    cliente, peticiones = cliente_falso([200])
    descargar(cliente, URL)
    assert peticiones[0].headers["User-Agent"].startswith("PriceTrackerBot/")


def test_reintenta_si_la_tienda_falla_temporalmente():
    cliente, peticiones = cliente_falso([503, 200])
    reloj = RelojFalso()

    assert descargar(cliente, URL, dormir=reloj) == "<html>200</html>"
    assert len(peticiones) == 2
    assert reloj.esperas == [2.0]


def test_reintenta_si_hay_error_de_red():
    cliente, _ = cliente_falso([httpx.ConnectError("sin conexión"), 200])
    assert descargar(cliente, URL, dormir=RelojFalso()) == "<html>200</html>"


def test_espera_exponencial_y_se_rinde_al_final():
    cliente, peticiones = cliente_falso([503, 503, 503])
    reloj = RelojFalso()

    with pytest.raises(DescargaError, match="3 intentos"):
        descargar(cliente, URL, dormir=reloj)
    assert len(peticiones) == 3
    assert reloj.esperas == [2.0, 4.0]  # entre el 1.º y 2.º, y entre el 2.º y 3.º


def test_no_reintenta_si_la_pagina_no_existe():
    cliente, peticiones = cliente_falso([404])
    reloj = RelojFalso()

    with pytest.raises(DescargaError, match="404"):
        descargar(cliente, URL, dormir=reloj)
    assert len(peticiones) == 1  # un 404 no se arregla reintentando
    assert reloj.esperas == []


def test_avisa_en_el_log_cada_reintento(caplog):
    cliente, _ = cliente_falso([503, 200])
    descargar(cliente, URL, dormir=RelojFalso())
    assert "Intento 1 de 3 falló: HTTP 503" in caplog.text
