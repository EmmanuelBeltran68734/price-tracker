from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductoExtraido:
    """Datos de un producto leído de su página, ya limpios y normalizados."""

    nombre: str
    precio: Decimal
    moneda: str = "COP"
    disponible: bool = True
    imagen_url: str | None = None
