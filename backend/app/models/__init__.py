"""Modelos de la base de datos.

Importarlos aquí los registra en Base.metadata y permite que Alembic los detecte.
"""

from app.models.base import Base
from app.models.crawler import EjecucionCrawler, HistorialPrecio, Producto, Tienda
from app.models.usuario import Rol, Usuario

__all__ = [
    "Base",
    "EjecucionCrawler",
    "HistorialPrecio",
    "Producto",
    "Rol",
    "Tienda",
    "Usuario",
]
