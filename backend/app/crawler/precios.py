import re
from decimal import Decimal, InvalidOperation

CENTAVOS = Decimal("0.01")


def normalizar_precio(valor: str | int | float | Decimal) -> Decimal:
    """Convierte un precio en cualquier formato a Decimal con 2 decimales."""
    if isinstance(valor, Decimal):
        numero = valor
    elif isinstance(valor, int | float):
        numero = Decimal(str(valor))
    else:
        numero = _texto_a_decimal(valor)
    if numero <= 0:
        raise ValueError(f"El precio debe ser mayor que cero: {valor!r}")
    return numero.quantize(CENTAVOS)


def _texto_a_decimal(texto: str) -> Decimal:
    limpio = re.sub(r"[^\d.,-]", "", texto)
    if not re.search(r"\d", limpio):
        raise ValueError(f"No se encontró un precio en: {texto!r}")
    limpio = _quitar_separadores_de_miles(limpio)
    try:
        return Decimal(limpio)
    except InvalidOperation as error:
        raise ValueError(f"Precio inválido: {texto!r}") from error


def _quitar_separadores_de_miles(texto: str) -> str:
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            return texto.replace(".", "").replace(",", ".")
        return texto.replace(",", "")
    for separador in (".", ","):
        if separador in texto:
            partes = texto.split(separador)
            if len(partes) > 2 or len(partes[-1]) == 3:
                return texto.replace(separador, "")
            return texto.replace(separador, ".")
    return texto
