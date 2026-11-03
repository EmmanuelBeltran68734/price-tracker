from decimal import Decimal

import pytest

from app.crawler.precios import normalizar_precio


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("$ 1.299.900", Decimal("1299900")),  # formato colombiano en pantalla
        ("$1.299.900,50", Decimal("1299900.50")),  # con centavos
        ("COP 49.900", Decimal("49900")),  # con código de moneda
        ("2999000.0", Decimal("2999000")),  # microdata de Alkosto
        ("1,299,900", Decimal("1299900")),  # formato en inglés
        (3299900, Decimal("3299900")),  # número entero (JSON-LD de Éxito)
        (49900.5, Decimal("49900.50")),  # número con decimales
    ],
)
def test_normalizar_precio_convierte_formatos(entrada, esperado):
    assert normalizar_precio(entrada) == esperado


def test_normalizar_precio_devuelve_decimal():
    assert isinstance(normalizar_precio("$ 1.000"), Decimal)


@pytest.mark.parametrize("entrada", ["", "   ", "Agotado", "$"])
def test_normalizar_precio_rechaza_valores_invalidos(entrada):
    with pytest.raises(ValueError):
        normalizar_precio(entrada)
