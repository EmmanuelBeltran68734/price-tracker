from decimal import Decimal

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.crawler.modelos import ProductoExtraido
from app.crawler.repositorio import guardar_precio
from app.models import Base, HistorialPrecio, Producto, Tienda

TV = ProductoExtraido(nombre="Televisor LG 75", precio=Decimal("3299900.00"))


@pytest.fixture
def sesion():
    """Base de datos SQLite en memoria: se crea vacía para cada test y luego desaparece."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as sesion:
        yield sesion


def contar(sesion, modelo):
    return sesion.scalar(select(func.count()).select_from(modelo))


def test_guardar_precio_crea_tienda_producto_y_precio(sesion):
    guardar_precio(sesion, "https://www.exito.com/tv-lg/p", TV)
    sesion.commit()

    producto = sesion.scalar(select(Producto))
    assert producto.url == "https://www.exito.com/tv-lg/p"
    assert producto.nombre == "Televisor LG 75"
    assert producto.tienda.nombre == "Éxito"
    assert producto.precios[0].precio == Decimal("3299900.00")


def test_mismo_producto_con_otra_url_no_se_duplica(sesion):
    guardar_precio(sesion, "https://www.exito.com/tv-lg/p", TV)
    guardar_precio(sesion, "https://WWW.EXITO.COM/tv-lg/p?utm_source=facebook", TV)
    sesion.commit()

    assert contar(sesion, Producto) == 1  # un solo producto...
    assert contar(sesion, HistorialPrecio) == 2  # ...con dos precios en su historial


def test_productos_de_la_misma_tienda_comparten_tienda(sesion):
    guardar_precio(sesion, "https://www.exito.com/tv-lg/p", TV)
    guardar_precio(sesion, "https://www.exito.com/nevera/p", TV)
    sesion.commit()

    assert contar(sesion, Producto) == 2
    assert contar(sesion, Tienda) == 1
