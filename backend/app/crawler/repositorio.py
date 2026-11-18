"""Guarda en la base de datos lo que lee el crawler."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawler.modelos import ProductoExtraido
from app.crawler.urls import dominio_de, normalizar_url
from app.models import HistorialPrecio, Producto, Tienda

NOMBRES_TIENDAS = {"exito.com": "Éxito", "alkosto.com": "Alkosto"}


def obtener_o_crear_tienda(sesion: Session, dominio: str) -> Tienda:
    """Busca la tienda por dominio; si no existe, la crea."""
    tienda = sesion.scalar(select(Tienda).where(Tienda.dominio == dominio))
    if tienda is None:
        tienda = Tienda(nombre=NOMBRES_TIENDAS.get(dominio, dominio), dominio=dominio)
        sesion.add(tienda)
    return tienda


def obtener_o_crear_producto(sesion: Session, url: str) -> Producto:
    """Busca el producto por su URL normalizada; si no existe, lo crea."""
    url = normalizar_url(url)
    producto = sesion.scalar(select(Producto).where(Producto.url == url))
    if producto is None:
        tienda = obtener_o_crear_tienda(sesion, dominio_de(url))
        producto = Producto(url=url, tienda=tienda)
        sesion.add(producto)
    return producto


def guardar_precio(sesion: Session, url: str, datos: ProductoExtraido) -> HistorialPrecio:
    """Agrega una fila al historial de precios del producto (sin hacer commit)."""
    producto = obtener_o_crear_producto(sesion, url)
    producto.nombre = datos.nombre
    producto.imagen_url = datos.imagen_url

    registro = HistorialPrecio(
        precio=datos.precio, moneda=datos.moneda, disponible=datos.disponible
    )
    producto.precios.append(registro)
    return registro
